create database if not exists sharemap;
use sharemap;

DROP TABLE IF EXISTS `users`;
DROP TABLE IF EXISTS `comments`;
DROP TABLE IF EXISTS `maps`;
DROP TABLE IF EXISTS `markers`;
DROP TABLE IF EXISTS `members`;


CREATE TABLE `maps` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mode` enum('private','public') NOT NULL,
  `title` varchar(50) NOT NULL,
  `create_day` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `disable_map` enum('enable','disable') DEFAULT 'enable',
  `hash_code` varchar(35) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB ;

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
) ENGINE=InnoDB ;


CREATE TABLE `markers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `map_id` int(11) NOT NULL,
  `lat` varchar(35) NOT NULL,
  `lng` varchar(35) NOT NULL,
  `date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `title` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
   FOREIGN KEY (`map_id`) REFERENCES `maps` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB ;

CREATE TABLE `members` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `map_id` int(11) DEFAULT NULL,
  `role` enum('admin','user') NOT NULL DEFAULT 'user',
  `join_day` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `ban` tinyint(1) DEFAULT '0',
  `email` varchar(35) NOT NULL,
  PRIMARY KEY (`id`),
   FOREIGN KEY (`email`) REFERENCES `users` (`email`),
   FOREIGN KEY (`map_id`) REFERENCES `maps` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB ;


CREATE TABLE `comments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `map_id` int(11) DEFAULT NULL,
  `markerId` int(11) DEFAULT NULL,
  `username` varchar(35) NOT NULL,
  `msg` varchar(100) NOT NULL,
  `datetime` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`markerId`) REFERENCES `markers` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
   FOREIGN KEY (`map_id`) REFERENCES `maps` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB ;

