# -*- coding: utf-8 -*-
"""MySQL 数据库访问层（基于 PyMySQL）"""
import pymysql
from pymysql.cursors import DictCursor

from config import DB_CONFIG

_SCHEMA_SQL = """
CREATE DATABASE IF NOT EXISTS `pdf_summary`
  DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_general_ci;
"""

_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS `pdf_document` (
  `id`             INT          NOT NULL AUTO_INCREMENT,
  `original_name`  VARCHAR(255) NOT NULL,
  `stored_name`    VARCHAR(255) NOT NULL,
  `file_size`      INT          DEFAULT 0,
  `page_count`     INT          DEFAULT 0,
  `char_count`     INT          DEFAULT 0,
  `sentence_count` INT          DEFAULT 0,
  `para_count`     INT          DEFAULT 0,
  `summary`        TEXT,
  `status`         TINYINT      DEFAULT 2,
  `create_time`    DATETIME     DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `pdf_keyword` (
  `id`          INT          NOT NULL AUTO_INCREMENT,
  `document_id` INT          NOT NULL,
  `keyword`     VARCHAR(100) NOT NULL,
  `weight`      FLOAT        DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `idx_doc` (`document_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `pdf_paragraph` (
  `id`             INT   NOT NULL AUTO_INCREMENT,
  `document_id`    INT   NOT NULL,
  `para_no`        INT   NOT NULL,
  `content`        TEXT,
  `sentence_count` INT   DEFAULT 0,
  `char_count`     INT   DEFAULT 0,
  `score`          FLOAT DEFAULT 0,
  `key_sentence`   TEXT,
  PRIMARY KEY (`id`),
  KEY `idx_doc` (`document_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""


def _connect(database=None):
    """建立数据库连接。database 为 None 时连接 MySQL 服务本身（不指定库）。"""
    cfg = dict(DB_CONFIG)
    if database is None:
        cfg.pop('database', None)
    else:
        cfg['database'] = database
    return pymysql.connect(**cfg)


def get_connection():
    """获取带 dict 游标的业务连接。"""
    return _connect(database=DB_CONFIG['database'])


def init_db():
    """启动时自动创建数据库与数据表（幂等，可重复执行）。"""
    # 1. 创建数据库
    conn = _connect(database=None)
    try:
        with conn.cursor() as cur:
            cur.execute(_SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()

    # 2. 创建数据表
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for stmt in _TABLES_SQL.split(';'):
                stmt = stmt.strip()
                if stmt:
                    cur.execute(stmt)
        conn.commit()
    finally:
        conn.close()


def query(sql, args=None):
    """执行查询，返回 dict 列表。"""
    conn = get_connection()
    try:
        with conn.cursor(DictCursor) as cur:
            cur.execute(sql, args or ())
            return cur.fetchall()
    finally:
        conn.close()


def query_one(sql, args=None):
    rows = query(sql, args)
    return rows[0] if rows else None


def execute(sql, args=None):
    """执行写操作，返回受影响行数。"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            n = cur.execute(sql, args or ())
        conn.commit()
        return n
    finally:
        conn.close()


def execute_insert(sql, args=None):
    """执行插入并返回自增主键。"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args or ())
            conn.commit()
            return cur.lastrowid
    finally:
        conn.close()
