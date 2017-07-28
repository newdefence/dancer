CREATE DATABASE  IF NOT EXISTS `db_dancer` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;
USE `db_dancer`;
-- MySQL dump 10.13  Distrib 5.7.9, for osx10.9 (x86_64)
--
-- Host: 127.0.0.1    Database: db_dancer
-- ------------------------------------------------------
-- Server version	5.7.11

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `blog`
--

DROP TABLE IF EXISTS `blog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `blog` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `uid` varchar(45) NOT NULL COMMENT '作者id',
  `title` varchar(256) DEFAULT NULL COMMENT '标题，或者 type=?表示阅后即焚？',
  `desc` varchar(2048) DEFAULT NULL COMMENT '正文内容',
  `img` varchar(64) DEFAULT NULL COMMENT '动态图片地址（不存域名）',
  `location` varchar(256) DEFAULT NULL COMMENT '地理信息，文字描述？和title是否重复？',
  `coordinate` varchar(45) DEFAULT NULL COMMENT '地理信息，经纬度，格式：x,y',
  `type` varchar(45) DEFAULT NULL COMMENT '普通图文，还是阅后即焚？',
  `status` int(11) DEFAULT NULL COMMENT '删除状态，1表示删除，是否需要有草稿状态？',
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `uid_index` (`uid`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户发布的动态：likeCount, viewCount 不做存储，直接从 blog_stat 中查询总量即可；后期可以把值存到 redis 中做优化';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `blog_likes`
--

DROP TABLE IF EXISTS `blog_likes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `blog_likes` (
  `blogId` int(11) NOT NULL,
  `likeUid` varchar(45) NOT NULL COMMENT '点赞者id',
  `likeTime` bigint(20) NOT NULL COMMENT '点赞时间，精确到秒',
  KEY `index1` (`blogId`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='点赞记录表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `blog_views`
--

DROP TABLE IF EXISTS `blog_views`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `blog_views` (
  `blogId` int(11) NOT NULL,
  `viewUid` varchar(45) NOT NULL COMMENT '查看者ID',
  `viewTime` bigint(20) NOT NULL COMMENT '查看时间（精确到秒）',
  KEY `index1` (`blogId`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='动态查看记录';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `chat`
--

DROP TABLE IF EXISTS `chat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `chat` (
  `fromUid` varchar(45) NOT NULL,
  `toUid` varchar(45) NOT NULL,
  `time` bigint(20) NOT NULL COMMENT '精确到毫秒',
  `type` int(11) NOT NULL COMMENT '聊天消息类型：0文本（包含emoji表情）1图片（msg是图片路径，大小，宽高）；2语音（msg是语音时长，大小？，路径含格式）；3.视频（msg是截图？视频大小，时长，宽高？）4.语音通话（通话时长）5.视频通话（msg是通话时长）',
  `msg` varchar(45) NOT NULL COMMENT '具体格式参考 msgType',
  KEY `index1` (`fromUid`,`toUid`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户聊天信息存储（存储条数和存储天数需要限制一下）';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `uid` varchar(32) NOT NULL COMMENT '用户uid，使用注册毫秒时间戳（重复的可能性很小，主要是缩减长度）然后16进制字符串存储',
  `phone` varchar(32) NOT NULL COMMENT '用户手机号，暂时不允许为空，暂时只支持大陆手机号（是否需要和 uid 联合约束？）',
  `name` varchar(128) NOT NULL COMMENT '用户昵称（128字节，大约能存33字符）',
  `createTime` bigint(20) NOT NULL COMMENT '用户创建时间戳（精确到毫秒, 1000*python:time.time()）',
  `passwd` varchar(45) DEFAULT NULL COMMENT '用户密码（使用手机验证码登录，可为空，存储方式为：md5(手机号:原始密码)）',
  `token` varchar(45) NOT NULL COMMENT '用户提交数据所需密码（不用每次都带着密码，生成方式：hex(登录精确到秒时间戳)-hex(100000至1000000随机数)）',
  `img` varchar(45) DEFAULT NULL COMMENT '用户图片地址：存储路径格式：uid/avatar/时间戳.后缀名（用户所有的上传的图片都存到一个历史记录表中）',
  PRIMARY KEY (`uid`,`phone`),
  UNIQUE KEY `uid_UNIQUE` (`uid`),
  UNIQUE KEY `telphone_UNIQUE` (`phone`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户核心信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_avatars`
--

DROP TABLE IF EXISTS `user_avatars`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_avatars` (
  `uid` varchar(32) NOT NULL,
  `img` varchar(45) NOT NULL COMMENT '图片路径（规则参考 user 表）',
  `createTime` bigint(20) NOT NULL COMMENT '图片上传时间（只有最后一个在使用，保存此信息主要是为了扩展业务，例如审核等）',
  KEY `index1` (`uid`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户上传的头像信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_follows`
--

DROP TABLE IF EXISTS `user_follows`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_follows` (
  `uid` varchar(45) NOT NULL COMMENT '当前用户id',
  `followUid` varchar(45) NOT NULL COMMENT '我关注的人的 id',
  `followTime` bigint(20) DEFAULT NULL COMMENT '关注的时间（精确到秒）',
  UNIQUE KEY `index1` (`uid`,`followUid`),
  KEY `index2` (`uid`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户关注信息表，uid和followUid唯一索引';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-07-29  0:18:06
