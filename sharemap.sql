-- MySQL dump 10.13  Distrib 8.0.12, for Linux (x86_64)
--
-- Host: localhost    Database: sharemap
-- ------------------------------------------------------
-- Server version	8.0.12

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
 SET NAMES utf8mb4 ;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `comments`
--

DROP TABLE IF EXISTS `comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `comments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `map_id` int(11) DEFAULT NULL,
  `markerId` int(11) DEFAULT NULL,
  `username` varchar(35) NOT NULL,
  `msg` varchar(100) NOT NULL,
  `datetime` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `markerId` (`markerId`),
  KEY `map_id` (`map_id`),
  CONSTRAINT `comments_ibfk_2` FOREIGN KEY (`markerId`) REFERENCES `markers` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `comments_ibfk_3` FOREIGN KEY (`map_id`) REFERENCES `maps` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comments`
--

LOCK TABLES `comments` WRITE;
/*!40000 ALTER TABLE `comments` DISABLE KEYS */;
INSERT INTO `comments` VALUES (1,21,3,'klados','ceid','2018-10-05 19:19:54'),(2,21,3,'klados','haha','2018-10-05 19:43:23'),(3,21,3,'klados','nnn','2018-10-05 19:44:35'),(4,21,3,'klados','tt','2018-10-05 19:45:29'),(7,21,3,'klados','zcv','2018-10-05 20:04:10'),(8,21,22,'admin','test','2018-10-06 23:49:29'),(9,21,22,'klados','tesr1','2018-10-06 23:50:29'),(10,21,22,'admin','xaxa','2018-10-06 23:50:35'),(11,20,36,'klados','hhh','2018-10-07 10:12:23'),(12,20,36,'klados','κάτι','2018-10-07 10:12:32'),(13,20,35,'klados','xaxa','2018-10-07 10:22:10'),(14,20,44,'klados','test','2018-10-07 12:31:23');
/*!40000 ALTER TABLE `comments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `maps`
--

DROP TABLE IF EXISTS `maps`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `maps` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mode` enum('private','public') NOT NULL,
  `title` varchar(50) NOT NULL,
  `create_day` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `disable_map` enum('enable','disable') DEFAULT 'enable',
  `hash_code` varchar(35) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `maps`
--

LOCK TABLES `maps` WRITE;
/*!40000 ALTER TABLE `maps` DISABLE KEYS */;
INSERT INTO `maps` VALUES (20,'public','test access map','2018-09-08 08:28:08','enable','7acabc8e074b44088b9744e509742215'),(21,'private','my map','2018-09-08 08:28:36','enable','e6b9e7c4c5368380df53f3fad13d7f64');
/*!40000 ALTER TABLE `maps` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `markers`
--

DROP TABLE IF EXISTS `markers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `markers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `map_id` int(11) NOT NULL,
  `lat` varchar(35) NOT NULL,
  `lng` varchar(35) NOT NULL,
  `date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `title` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `map_id` (`map_id`),
  CONSTRAINT `markers_ibfk_1` FOREIGN KEY (`map_id`) REFERENCES `maps` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `markers`
--

LOCK TABLES `markers` WRITE;
/*!40000 ALTER TABLE `markers` DISABLE KEYS */;
INSERT INTO `markers` VALUES (3,21,'38.2849037624818','21.787731979053','2018-10-04 22:05:18','ceid'),(13,21,'38.2564446348378','21.7616825175155','2018-10-06 19:51:14','test6'),(14,21,'38.2391888114571','21.6947849731446','2018-10-06 20:08:48','water'),(15,21,'38.2356638014971','21.7033680419922','2018-10-06 20:09:06','water2'),(16,21,'38.2194817807063','21.6982182006836','2018-10-06 20:09:27','water3'),(17,21,'38.2127575965983','21.6851719360352','2018-10-06 20:09:39','water4'),(18,21,'38.3343155012602','21.762762878418','2018-10-06 20:16:20','antirio'),(19,21,'38.3353927096371','21.7442234497071','2018-10-06 21:17:21','kastro'),(20,21,'38.3526065159011','21.7720325927735','2018-10-06 21:17:30','kastro2'),(21,21,'38.3286405384488','21.7826755981446','2018-10-06 21:18:14','nero'),(22,21,'38.3159811492958','21.7504890899659','2018-10-06 21:18:32','barka'),(23,21,'38.3017030159509','21.6982182006836','2018-10-06 21:53:42','blue'),(25,21,'38.2736967487239','21.6940983276368','2018-10-06 22:16:52','asdf'),(27,21,'38.3275825860861','21.6697224121094','2018-10-06 22:18:36','dasfasdf'),(28,21,'38.158786547654','21.7181309204102','2018-10-06 22:19:10','uea'),(29,21,'38.1541971647988','21.7974384765625','2018-10-06 22:20:51','xaxa'),(30,21,'38.1495880892942','21.775723312378','2018-10-06 22:21:10','something'),(31,21,'38.3499141048304','21.8591507415772','2018-10-06 22:23:05','vau'),(32,21,'38.3986312516607','21.7716892700196','2018-10-06 22:23:48','zaza'),(33,21,'38.3951333234661','21.8406971435547','2018-10-06 22:26:46','nafpaktos'),(34,21,'38.3846578646216','21.8355473022461','2018-10-06 22:27:00','nafpaktos2'),(35,20,'38.2463939427312','21.7347637368231','2018-10-07 10:01:51','patra'),(36,20,'38.2506573507349','21.7326394272833','2018-10-07 10:10:50','μώλος'),(37,20,'38.3029437844115','21.7806156616211','2018-10-07 10:12:54','ριο'),(38,20,'38.3121035081903','21.7346962432862','2018-10-07 10:13:52','test'),(39,20,'38.3869543135277','21.830483291626','2018-10-07 11:49:25','length'),(40,20,'38.3592308428513','21.8480785827637','2018-10-07 12:13:57','xaxa'),(41,20,'38.3562694561135','21.7886837463379','2018-10-07 12:16:30','sese'),(42,20,'38','21','2018-10-07 12:22:20','mmmk'),(43,20,'38.3794188873574','21.9163139801026','2018-10-07 12:22:46','xi'),(44,20,'38.49362659062288','21.802615405533743','2018-10-07 12:25:37','st');
/*!40000 ALTER TABLE `markers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `members`
--

DROP TABLE IF EXISTS `members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `members` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `map_id` int(11) DEFAULT NULL,
  `role` enum('admin','user') NOT NULL DEFAULT 'user',
  `join_day` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `ban` tinyint(1) DEFAULT '0',
  `email` varchar(35) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `email` (`email`),
  KEY `map_id` (`map_id`),
  CONSTRAINT `members_ibfk_1` FOREIGN KEY (`email`) REFERENCES `users` (`email`),
  CONSTRAINT `members_ibfk_2` FOREIGN KEY (`map_id`) REFERENCES `maps` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `members`
--

LOCK TABLES `members` WRITE;
/*!40000 ALTER TABLE `members` DISABLE KEYS */;
INSERT INTO `members` VALUES (1,20,'admin','2018-09-08 08:28:08',0,'georklad@hotmail.com'),(2,21,'admin','2018-09-08 08:28:36',0,'georklad@hotmail.com'),(10,21,'user','2018-10-07 09:40:17',0,'admin@admin.com');
/*!40000 ALTER TABLE `members` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(35) NOT NULL,
  `fullname` varchar(35) NOT NULL,
  `email` varchar(35) NOT NULL,
  `password` varchar(100) NOT NULL,
  `join_day` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'klados','George klados','georklad@hotmail.com','202cb962ac59075b964b07152d234b70','2018-09-02 15:07:46'),(2,'admin','admin','admin@admin.com','202cb962ac59075b964b07152d234b70','2018-09-08 08:34:31');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-10-07 18:20:51
