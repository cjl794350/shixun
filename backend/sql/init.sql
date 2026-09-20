-- ============================================================
--  PDF智能摘要工具 数据库初始化脚本
--  数据库: pdf_summary
--  账号/密码: root / root  (由后端 config.py 读取)
--  字符集: utf8mb4  存储引擎: InnoDB
--  使用方法: mysql -uroot -proot < init.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS `pdf_summary`
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_general_ci;

USE `pdf_summary`;

-- ------------------------------------------------------------
-- 文档表: 记录上传的论文 PDF 及其整体分析结果
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `pdf_document` (
  `id`            INT           NOT NULL AUTO_INCREMENT COMMENT '文档主键',
  `original_name` VARCHAR(255)  NOT NULL COMMENT '原始文件名',
  `stored_name`   VARCHAR(255)  NOT NULL COMMENT '服务器存储文件名(uuid.pdf)',
  `file_size`     INT           DEFAULT 0 COMMENT '文件大小(字节)',
  `page_count`    INT           DEFAULT 0 COMMENT 'PDF 页数',
  `char_count`    INT           DEFAULT 0 COMMENT '正文字符数',
  `sentence_count` INT          DEFAULT 0 COMMENT '句子总数',
  `para_count`    INT           DEFAULT 0 COMMENT '段落总数',
  `summary`       TEXT          COMMENT '自动生成的全文摘要',
  `status`        TINYINT       DEFAULT 2 COMMENT '状态: 1=处理中 2=完成 3=失败',
  `create_time`   DATETIME      DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
  PRIMARY KEY (`id`),
  KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='上传的论文文档及整体分析结果';

-- ------------------------------------------------------------
-- 关键词表: 存储每篇论文提取出的关键词及其权重
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `pdf_keyword` (
  `id`          INT           NOT NULL AUTO_INCREMENT COMMENT '主键',
  `document_id` INT           NOT NULL COMMENT '所属文档ID',
  `keyword`     VARCHAR(100)  NOT NULL COMMENT '关键词',
  `weight`      FLOAT         DEFAULT 0 COMMENT 'TF-IDF 权重',
  PRIMARY KEY (`id`),
  KEY `idx_doc` (`document_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='论文关键词及权重';

-- ------------------------------------------------------------
-- 段落表: 存储每篇论文逐段分析结果
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `pdf_paragraph` (
  `id`             INT      NOT NULL AUTO_INCREMENT COMMENT '主键',
  `document_id`    INT      NOT NULL COMMENT '所属文档ID',
  `para_no`        INT      NOT NULL COMMENT '段落序号(从1开始)',
  `content`        TEXT     COMMENT '段落原文',
  `sentence_count` INT      DEFAULT 0 COMMENT '段落句数',
  `char_count`     INT      DEFAULT 0 COMMENT '段落字数',
  `score`          FLOAT    DEFAULT 0 COMMENT '段落重要度评分(TextRank)',
  `key_sentence`   TEXT     COMMENT '段落关键句',
  PRIMARY KEY (`id`),
  KEY `idx_doc` (`document_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='论文逐段分析结果';
