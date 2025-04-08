CREATE DATABASE IF NOT EXISTS qa_platform;

CREATE TABLE IF NOT EXISTS `test_sku_info` (
  `id` int(5) NOT NULL AUTO_INCREMENT,
  `course_id` int(16) DEFAULT NULL COMMENT '课程id',
  `course_name` varchar(50) DEFAULT NULL COMMENT '课程名称',
  `course_type` tinyint(1) DEFAULT NULL COMMENT '课程类型：1-体验课、2-正式课、3-特训课',
  'sku_type' tinyint(1) DEFAULT NULL COMMENT '商品类型'：1-旧商品V1、2-新商品V2,
  `sku_id` int(16) DEFAULT NULL COMMENT 'sku_id',
  `sku_name` varchar(50) DEFAULT NULL COMMENT 'sku名称',
  `sku_price` float DEFAULT NULL COMMENT 'sku优惠价',
  `env` tinyint(1) DEFAULT NULL COMMENT '环境：1-测试、2-正式',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `status` bit(1) DEFAULT b'1' COMMENT '状态: 0-无效 1-有效',
  `source` tinyint(1) NOT NULL DEFAULT '0' COMMENT '来源：0-sql导入、1-页面创建、2-页面导入',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC COMMENT='sku记录';

