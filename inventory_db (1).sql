-- MySQL dump 10.13  Distrib 8.0.34, for Win64 (x86_64)
--
-- Host: localhost    Database: inventory_system
-- ------------------------------------------------------
-- Server version	8.0.35

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `branches`
--

DROP TABLE IF EXISTS `branches`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `branches` (
  `branch_id` int NOT NULL AUTO_INCREMENT,
  `branch_name` varchar(100) NOT NULL,
  `branch_address` varchar(255) NOT NULL,
  PRIMARY KEY (`branch_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `branches`
--

LOCK TABLES `branches` WRITE;
/*!40000 ALTER TABLE `branches` DISABLE KEYS */;
INSERT INTO `branches` VALUES (1,'FOX','Haifa'),(2,'FOX-Home','Tel-Aviv');
/*!40000 ALTER TABLE `branches` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customers`
--

DROP TABLE IF EXISTS `customers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customers` (
  `customer_id` int NOT NULL AUTO_INCREMENT,
  `customer_name` varchar(255) NOT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `password_hash` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`customer_id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customers`
--

LOCK TABLES `customers` WRITE;
/*!40000 ALTER TABLE `customers` DISABLE KEYS */;
INSERT INTO `customers` VALUES (1,'dfdh','dhf','dhf',NULL),(2,'sdfh','346','rhe',NULL),(3,'sdv','235','weg',NULL),(4,'shfdf','346','ryhs',NULL),(5,'dfs','235','dsgd',NULL),(6,'sdg','5325','sgddsg',NULL),(7,'ahmad','34634467','dfndrn',NULL),(8,'shakata','32626','egherh',NULL),(9,'dfs','235','dsgd',NULL),(10,'ahmad','52453','gsrwe@gmail.com',NULL),(11,'sdgsg','055883468','fjgxg@gmail.com',NULL),(12,'guy','658568','ehs@gsdg',NULL),(13,'marah','0648458448','marah43y@gmail.com',NULL),(14,'amir','05666481','rhjre34@gmail.com',NULL),(15,'sari','735377205','dfjej@gmail.com',NULL),(16,'afsw','54848648','sdb@gmail.com',NULL),(17,'tafa','783783','fgsmrfmg',NULL),(18,'aegew','436','dsbrb',NULL),(19,'ahmad mostafa shalata','0533071442','shalataahmad10@gmail.com',NULL),(20,'malek','0264811','mal4eks@gmail.com','15e2b0d3c33891ebb0f1ef609ec419420c20e320ce94c65fbc8c3312448eb225');
/*!40000 ALTER TABLE `customers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `employees`
--

DROP TABLE IF EXISTS `employees`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `employees` (
  `employee_id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(50) DEFAULT NULL,
  `last_name` varchar(50) DEFAULT NULL,
  `address` varchar(100) DEFAULT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `username` varchar(50) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `hourly_rate` decimal(10,2) DEFAULT NULL,
  `branch_id` int DEFAULT NULL,
  `role` enum('manager','worker') DEFAULT 'worker',
  PRIMARY KEY (`employee_id`),
  UNIQUE KEY `username` (`username`),
  KEY `fk_employees_branch` (`branch_id`),
  CONSTRAINT `fk_employees_branch` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`branch_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employees`
--

LOCK TABLES `employees` WRITE;
/*!40000 ALTER TABLE `employees` DISABLE KEYS */;
INSERT INTO `employees` VALUES (1,'ahmad','shalata','sakhnin','0533071442','shalataahmad10@gmail.com','Ahmad11','Ahmadsh11',50.00,1,'manager'),(2,'rymym','rym','rym','782','ghm','aa','1234',20.00,2,'worker');
/*!40000 ALTER TABLE `employees` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `expenses`
--

DROP TABLE IF EXISTS `expenses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `expenses` (
  `expense_id` int NOT NULL AUTO_INCREMENT,
  `branch_id` int DEFAULT NULL,
  `sku` varchar(50) DEFAULT NULL,
  `item_name` varchar(100) DEFAULT NULL,
  `quantity_added` int DEFAULT NULL,
  `unit_price` decimal(10,2) DEFAULT NULL,
  `total_cost` decimal(10,2) DEFAULT NULL,
  `expense_date` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`expense_id`),
  KEY `branch_id` (`branch_id`),
  CONSTRAINT `expenses_ibfk_1` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`branch_id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `expenses`
--

LOCK TABLES `expenses` WRITE;
/*!40000 ALTER TABLE `expenses` DISABLE KEYS */;
INSERT INTO `expenses` VALUES (1,1,'2','Jeans',9,49.99,449.91,'2025-04-13 16:51:22'),(2,1,'12','fox racing',10,9.99,99.90,'2025-04-13 17:25:04'),(3,1,'34','reg',25,345.00,8625.00,'2025-04-13 17:25:28'),(4,2,'22','Scarlet',20,11.99,239.80,'2025-04-13 17:25:55'),(5,2,'111','ewrr',12,24.99,299.88,'2025-04-13 17:26:13'),(6,2,'535','shirts',15,45.00,675.00,'2025-04-13 19:35:22'),(7,1,'42','shorts',5,44.99,224.95,'2025-04-14 15:34:35'),(8,1,'12','fox racing',20,9.99,199.80,'2025-04-16 11:42:35'),(9,1,'42','shorts',45,44.99,2024.55,'2025-04-16 17:08:14'),(10,1,'1','sdv',5,345.99,1729.95,'2025-04-16 19:48:17'),(11,2,'111','ewrr',5,24.99,124.95,'2025-04-16 20:03:30'),(12,2,'535','shirts',2,45.00,90.00,'2025-04-16 20:05:06'),(13,1,'2','Jeans',5,49.99,249.95,'2025-04-16 20:07:04'),(14,2,'99','rgwg',1,33.00,33.00,'2025-04-16 21:12:24'),(15,2,'2352','herhe',10,355.99,3559.90,'2025-04-20 09:04:22'),(16,2,'22','Scarlet',3,11.99,35.97,'2025-04-23 20:01:35'),(17,2,'111','ewrr',2,24.99,49.98,'2025-04-23 21:59:27'),(18,2,'111','ewrr',2,24.99,49.98,'2025-04-29 11:23:40'),(19,1,'2','Jeans',5,1.99,9.95,'2025-05-01 10:13:59'),(20,2,'111','ewrr',1,24.99,24.99,'2025-05-03 20:30:37');
/*!40000 ALTER TABLE `expenses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory`
--

DROP TABLE IF EXISTS `inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inventory` (
  `sku` varchar(50) NOT NULL,
  `item_name` varchar(255) DEFAULT NULL,
  `category` varchar(100) NOT NULL,
  `quantity` int NOT NULL DEFAULT '0',
  `price` decimal(10,2) NOT NULL,
  `branch_id` int DEFAULT NULL,
  `image_path` varchar(255) DEFAULT NULL,
  `color` varchar(50) DEFAULT NULL,
  `size` varchar(50) DEFAULT NULL,
  `shelf_row` int DEFAULT NULL,
  `shelf_column` int DEFAULT NULL,
  `last_updated` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_active` tinyint(1) DEFAULT '1',
  `received_date` date NOT NULL DEFAULT (curdate()),
  `shelf_zone` varchar(1) DEFAULT 'A',
  PRIMARY KEY (`sku`),
  KEY `fk_inventory_branch` (`branch_id`),
  CONSTRAINT `fk_inventory_branch` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`branch_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `inventory_ibfk_1` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`branch_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory`
--

LOCK TABLES `inventory` WRITE;
/*!40000 ALTER TABLE `inventory` DISABLE KEYS */;
INSERT INTO `inventory` VALUES ('1','sdv','sdbwb',13,345.99,1,'C:/Users/admin/OneDrive/תמונות/צילומי מסך/צילום מסך 2023-05-01 223710.png','Blue','XL',1,2,'2025-05-22 12:04:18',1,'2025-01-20','A'),('111','TTT','Clothing',27,9.99,2,'images\\צילום מסך 2025-04-09 105916.png','Blue','XL',8,6,'2025-06-11 17:38:12',1,'2025-01-25','B'),('12','fox racing','LongShirt',16,9.99,1,'images\\shirt_yellow.jpg','yellow','M',1,4,'2025-06-10 11:57:24',1,'2025-01-20','C'),('2','Jeans','Clothing',0,1.99,1,'C:/Users/admin/OneDrive/תמונות/צילומי מסך/צילום מסך 2024-02-10 220912.png','Blue','L',2,6,'2025-06-10 11:57:24',0,'2025-01-20','D'),('2121','sdsd','cloths',3705,21.12,1,'C:/Users/admin/OneDrive/תמונות/צילומי מסך/צילום מסך 2024-01-21 123124.png','yellow','S',8,4,'2025-06-11 17:41:40',1,'2025-01-13','B'),('22','Scarlet','short',9,11.99,2,'images\\f1348a64acc52399d77572d75e526d047a29eab9_original.jpeg','Black','M',2,5,'2025-06-10 11:57:24',1,'2025-01-25','F'),('221','shirt','short',535,18.61,2,'C:/Users/admin/OneDrive/שולחן העבודה/images.jpeg','Black','XL',1,1,'2025-06-10 11:57:24',1,'2025-01-16','G'),('235','weg','sgdvds',264,31.50,2,NULL,NULL,NULL,NULL,NULL,'2025-06-10 11:57:24',0,'2025-01-16','H'),('2352','herhe','jnrtj',13,355.99,2,'C:/Users/admin/OneDrive/תמונות/צילומי מסך/צילום מסך 2024-01-21 123124.png','Red','M',3,6,'2025-06-10 11:57:24',1,'2025-01-25','I'),('2355','whwe','clothing',33,12.99,2,'images\\צילום מסך 2025-04-09 105916.png','Black','XL',7,9,'2025-06-10 11:57:24',1,'2025-04-29','J'),('247','wbwy','bre',33,5.99,2,'images\\2025-04-17_134811.png','Black','M',6,6,'2025-05-29 14:16:58',0,'2025-01-29','B'),('253','wbre','webe',228,6.86,1,'images\\2025-03-13_204034.png','gvew','m',3,3,'2025-05-03 11:53:20',1,'2025-02-20','A'),('3','gvs','wegw',2371,325.00,1,'C:/Users/admin/OneDrive/תמונות/צילומי מסך/צילום מסך 2024-07-30 191917.png','Red','L',2,1,'2025-04-22 21:14:10',1,'2025-01-20','A'),('30','Swimwear','Swim',50,9.99,2,'images\\5138e8220884c69db6804468a5604172.jpg','Black','M',4,6,'2025-05-03 20:31:01',1,'2025-01-25','A'),('335','hteh','short',43,33.00,1,'images\\images (1).jpeg','yellow','L',3,4,'2025-04-30 16:43:58',1,'2025-04-30','A'),('34','reg','erg',27,345.00,1,'images\\shorrt.jpg','Yellow','L',3,5,'2025-05-01 17:08:35',1,'2025-01-25','A'),('3434','erh','Clothing',44,34.00,1,'images\\צילום מסך 2025-04-09 105916.png','black','M',6,5,'2025-05-01 12:18:12',1,'2025-04-25','A'),('344','sbr','rshb',23,33.00,2,'images\\צילום מסך 2024-07-30 144135.png','yellow','L',5,4,'2025-05-01 19:52:55',0,'2025-01-29','A'),('345453','cntr','rbreb',253,3.00,1,'images\\צילום מסך 2024-01-07 131538.png','red','L',7,8,'2025-05-01 12:18:12',1,'2025-01-13','A'),('346','ehrh','fdb',45,4170.60,2,'images\\צילום מסך 2025-04-07 190403.png','fdb','g',7,4,'2025-04-28 18:13:36',1,'2025-04-23','A'),('373','hrt','rtj',575,65.99,1,'images\\צילום מסך 2025-04-20 185514.png','we','m',2,6,'2025-04-23 15:05:38',1,'2025-04-23','A'),('42','shorts','short',37,44.99,2,'C:/Users/admin/OneDrive/שולחן העבודה/פרויקט גמר/InventoryManagementSystem/images/Shorts.jpg','Black','S',4,7,'2025-05-03 20:31:05',1,'2025-01-20','A'),('45','jersey','cloths',46,19.99,2,'images\\35cbe2d1be0b5574d51c3994181da2e0acda5b55_original.jpeg','Blue','XL',5,8,'2025-04-22 21:27:44',1,'2025-01-25','A'),('467','tnf','fgj',67,46.00,2,'images\\shirt_yellow.jpg','Black','L',5,2,'2025-05-03 20:30:55',0,'2025-05-03','A'),('535','shirts','short',22,45.00,1,'C:/Users/admin/OneDrive/תמונות/צילומי מסך/צילום מסך 2024-07-30 191917.png','Red','XL,M',5,3,'2025-06-10 10:25:34',1,'2025-01-29','A'),('56','fykf','Clothing',55,12.99,1,'images\\צילום מסך 2022-10-22 145202.png','Red','L',8,5,'2025-05-03 11:50:49',1,'2025-04-25','A'),('567','hfnh','jty',45,45.00,1,'images\\צילום מסך 2025-05-02 113921.png','thr','rht',8,1,'2025-05-03 13:15:36',1,'2025-05-03','A'),('5710840218385','T-shirt','clothing',50,5.99,2,'static/images\\צילום מסך 2025-01-23 180918.png','Silver','L',3,3,'2025-06-10 09:51:20',1,'2025-06-10','A'),('5902047172922','DARK HORSE','clothing',80,4.99,2,'images\\צילום מסך 2025-05-18 192611.png','Yellow','XL',8,3,'2025-05-20 11:53:13',1,'2025-05-20','A'),('5902047174261','Filter','Clothing',457,5.00,1,'C:/Users/admin/OneDrive/תמונות/צילומי מסך/צילום מסך 2025-01-11 145936.png','Silver','L',7,3,'2025-06-10 10:08:01',1,'2025-05-08','A'),('99','rgwg','dfn',47,33.00,2,'images\\צילום מסך 2024-01-07 131538.png','black','M',7,6,'2025-04-22 21:27:50',1,'2025-01-25','A');
/*!40000 ALTER TABLE `inventory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_items`
--

DROP TABLE IF EXISTS `order_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_items` (
  `order_item_id` int NOT NULL AUTO_INCREMENT,
  `order_id` int DEFAULT NULL,
  `sku` varchar(50) DEFAULT NULL,
  `item_name` varchar(100) DEFAULT NULL,
  `quantity` int DEFAULT NULL,
  `color` varchar(20) DEFAULT NULL,
  `size` varchar(10) DEFAULT NULL,
  `item_status` varchar(50) DEFAULT 'ממתין',
  PRIMARY KEY (`order_item_id`),
  KEY `order_id` (`order_id`),
  KEY `fk_order_items_sku` (`sku`),
  CONSTRAINT `fk_order_items_sku` FOREIGN KEY (`sku`) REFERENCES `inventory` (`sku`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `order_items_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `purchases` (`purchase_id`),
  CONSTRAINT `order_items_ibfk_2` FOREIGN KEY (`sku`) REFERENCES `inventory` (`sku`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_items`
--

LOCK TABLES `order_items` WRITE;
/*!40000 ALTER TABLE `order_items` DISABLE KEYS */;
INSERT INTO `order_items` VALUES (1,110,'221','shirt',2,'Black','XL','סיום המכלה'),(2,111,'111','TTT',3,'Blue','XL','סיום המכלה'),(3,111,'2121','sdsd',2,'yellow','S','סיום המכלה');
/*!40000 ALTER TABLE `order_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_notifications`
--

DROP TABLE IF EXISTS `order_notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_notifications` (
  `notification_id` int NOT NULL AUTO_INCREMENT,
  `order_id` int DEFAULT NULL,
  `is_read` tinyint(1) DEFAULT '0',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`notification_id`),
  KEY `fk_order_notifications_order` (`order_id`),
  CONSTRAINT `fk_order_notifications_order` FOREIGN KEY (`order_id`) REFERENCES `order_items` (`order_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `order_notifications_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `purchases` (`purchase_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_notifications`
--

LOCK TABLES `order_notifications` WRITE;
/*!40000 ALTER TABLE `order_notifications` DISABLE KEYS */;
INSERT INTO `order_notifications` VALUES (1,110,1,'2025-05-25 19:54:51'),(2,111,1,'2025-05-27 20:02:31');
/*!40000 ALTER TABLE `order_notifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `purchases`
--

DROP TABLE IF EXISTS `purchases`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `purchases` (
  `purchase_id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int DEFAULT NULL,
  `customer_name` varchar(255) DEFAULT NULL,
  `sku` varchar(50) DEFAULT NULL,
  `item_name` varchar(255) DEFAULT NULL,
  `quantity` int NOT NULL,
  `total_price` decimal(10,2) NOT NULL,
  `purchase_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `color` varchar(50) DEFAULT NULL,
  `size` varchar(50) DEFAULT NULL,
  `branch_name` varchar(255) DEFAULT NULL,
  `branch_address` varchar(255) DEFAULT NULL,
  `branch_id` int DEFAULT NULL,
  `order_status` varchar(50) DEFAULT 'הזמנה חדשה',
  PRIMARY KEY (`purchase_id`),
  KEY `item_id` (`item_name`),
  KEY `branch_id` (`branch_name`),
  KEY `fk_purchases_customer` (`customer_id`),
  KEY `fk_purchases_branch` (`branch_id`),
  KEY `fk_purchases_sku` (`sku`),
  CONSTRAINT `fk_branch` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`branch_id`),
  CONSTRAINT `fk_customer` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`),
  CONSTRAINT `fk_customers` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`),
  CONSTRAINT `fk_purchases_branch` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`branch_id`),
  CONSTRAINT `fk_purchases_customer` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`),
  CONSTRAINT `fk_purchases_sku` FOREIGN KEY (`sku`) REFERENCES `inventory` (`sku`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=112 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purchases`
--

LOCK TABLES `purchases` WRITE;
/*!40000 ALTER TABLE `purchases` DISABLE KEYS */;
INSERT INTO `purchases` VALUES (1,7,'ahmad','1','sdv',1,345.99,'2025-03-16 21:48:57',NULL,NULL,'2',NULL,NULL,'הזמנה חדשה'),(2,7,'ahmad','1','sdv',22,7611.78,'2025-03-16 21:57:11',NULL,NULL,'2',NULL,NULL,'הזמנה חדשה'),(3,8,'shakata','2','jeans',1,49.99,'2025-03-16 21:57:21',NULL,NULL,'1',NULL,NULL,'הזמנה חדשה'),(4,7,'ahmad','2','jeans',2,99.98,'2025-03-16 22:59:37',NULL,NULL,'1',NULL,NULL,'הזמנה חדשה'),(5,5,'dfs','2352','herhe',24,8543.76,'2025-03-17 21:26:01',NULL,NULL,'2',NULL,NULL,'הזמנה חדשה'),(6,7,'ahmad','235','weg',12,2820.00,'2025-03-18 18:11:52',NULL,NULL,'1',NULL,NULL,'הזמנה חדשה'),(7,7,'ahmad','1','sdv',33,11417.67,'2025-03-18 18:29:45',NULL,NULL,'2',NULL,NULL,'הזמנה חדשה'),(8,5,'dfs',NULL,'hher',22,7612.00,'2025-03-18 18:31:51',NULL,NULL,'FOX',NULL,NULL,'הזמנה חדשה'),(9,7,'ahmad','2121','sdsd',11,242.00,'2025-03-18 19:27:04',NULL,NULL,'1',NULL,NULL,'הזמנה חדשה'),(10,8,'shakata','2121','sdsd',13,286.00,'2025-03-18 19:27:56',NULL,NULL,'1',NULL,NULL,'הזמנה חדשה'),(11,7,'ahmad','1','sdv',11,3805.89,'2025-03-18 19:29:04',NULL,NULL,'2',NULL,NULL,'הזמנה חדשה'),(12,7,'ahmad','111','ewrr',22,549.78,'2025-03-18 21:37:52',NULL,NULL,'FOX-Home',NULL,NULL,'הזמנה חדשה'),(13,7,'ahmad',NULL,'vwnvo',222,5103.78,'2025-03-18 21:55:40',NULL,NULL,'FOX',NULL,NULL,'הזמנה חדשה'),(14,NULL,NULL,'1','sdv',11,3805.89,'2025-03-18 22:12:39',NULL,NULL,'FOX',NULL,NULL,'הזמנה חדשה'),(15,NULL,NULL,'1','sdv',122,42210.78,'2025-03-18 22:13:40',NULL,NULL,'FOX',NULL,NULL,'הזמנה חדשה'),(16,11,'sdgsg','235','weg',23,5405.00,'2025-03-18 23:04:43',NULL,NULL,'2',NULL,NULL,'הזמנה חדשה'),(17,NULL,'ahmads','1','sdv',22,7611.78,'2025-03-18 23:50:06',NULL,NULL,'2',NULL,NULL,'הזמנה חדשה'),(18,NULL,'rerg','235','weg',23,5405.00,'2025-03-18 23:51:05',NULL,NULL,'1',NULL,NULL,'הזמנה חדשה'),(19,7,'ahmad','1','sdv',23,7957.77,'2025-03-19 00:10:37',NULL,NULL,'FOX-Home',NULL,NULL,'הזמנה חדשה'),(20,NULL,'aboo','3','gvs',21,6825.00,'2025-03-19 22:20:42',NULL,NULL,'FOX',NULL,NULL,'הזמנה חדשה'),(21,NULL,'rfgb','1','sdv',3,1037.97,'2025-03-19 23:35:40',NULL,NULL,'FOX-Home',NULL,NULL,'הזמנה חדשה'),(22,NULL,'1','1','sdv',1,345.99,'2025-03-19 23:38:29',NULL,NULL,'FOX-Home',NULL,NULL,'הזמנה חדשה'),(23,7,'ahmad','1','sdv',1,345.99,'2025-03-20 18:50:48',NULL,NULL,'FOX-Home',NULL,NULL,'הזמנה חדשה'),(24,NULL,'ahmed','235','weg',2,470.00,'2025-03-20 21:22:46',NULL,NULL,'FOX',NULL,NULL,'הזמנה חדשה'),(25,NULL,'ahmed','1','sdv',2,691.98,'2025-03-20 21:23:34',NULL,NULL,'FOX-Home',NULL,NULL,'הזמנה חדשה'),(26,NULL,'ahmed','235','weg',1,235.00,'2025-03-20 21:27:59',NULL,NULL,'FOX',NULL,NULL,'הזמנה חדשה'),(27,NULL,'ahreh',NULL,'hher',1,346.00,'2025-03-20 21:28:56',NULL,NULL,'FOX',NULL,NULL,'הזמנה חדשה'),(28,7,'ahmad','42','fsaf',1,43.00,'2025-03-22 19:34:19',NULL,NULL,'FOX',NULL,NULL,'הזמנה חדשה'),(29,12,'guy','1','sdv',1,345.99,'2025-03-22 21:07:49',NULL,NULL,'FOX-Home',NULL,NULL,'הזמנה חדשה'),(30,12,'guy','1','sdv',3,1037.97,'2025-03-22 21:11:24',NULL,NULL,'FOX-Home',NULL,NULL,'הזמנה חדשה'),(31,7,'ahmad','1','sdv',3,1037.97,'2025-03-22 21:11:55',NULL,NULL,'FOX-Home',NULL,NULL,'הזמנה חדשה'),(32,8,'shakata','2','jeans',2,99.98,'2025-03-22 21:14:59',NULL,NULL,'FOX',NULL,NULL,'הזמנה חדשה'),(33,8,'shakata','1','sdv',1,345.99,'2025-03-22 21:40:03',NULL,NULL,'FOX-Home','Tel-Aviv',NULL,'הזמנה חדשה'),(34,3,'sdv','3','gvs',120,39000.00,'2025-03-22 22:08:01',NULL,NULL,'FOX','Haifa',NULL,'הזמנה חדשה'),(35,1,'dfdh','42','fsaf',5,215.00,'2025-03-22 22:09:10',NULL,NULL,'FOX','Haifa',NULL,'הזמנה חדשה'),(36,3,'sdv','34','reg',33,11385.00,'2025-03-22 23:12:07',NULL,NULL,'FOX','Haifa',NULL,'הזמנה חדשה'),(37,8,'shakata',NULL,'vwnvo',10,229.90,'2025-03-24 20:19:51',NULL,NULL,'FOX','Haifa',NULL,'הזמנה חדשה'),(38,11,'sdgsg','34','reg',22,7590.00,'2025-03-24 22:07:44',NULL,NULL,'FOX','Haifa',NULL,'הזמנה חדשה'),(39,8,'shakata','34','reg',10,3450.00,'2025-03-29 19:50:22',NULL,NULL,'FOX','Haifa',NULL,'הזמנה חדשה'),(40,8,'shakata','221','shirt',11,219.89,'2025-03-29 20:06:44',NULL,NULL,'FOX','Haifa',NULL,'הזמנה חדשה'),(41,8,'shakata','22','Scarlet',5,59.95,'2025-04-02 09:47:58',NULL,NULL,'FOX-Home','Tel-Aviv',NULL,'הזמנה חדשה'),(42,12,'guy','22','scarlet',1,11.99,'2025-04-03 08:57:12','2','Black','FOX-Home','Tel-Aviv',NULL,'הזמנה חדשה'),(43,14,'amir','22','scarlet',3,35.97,'2025-04-03 10:29:38','2','Black','FOX-Home','Tel-Aviv',NULL,'הזמנה חדשה'),(44,11,'sdgsg','22','scarlet',2,23.98,'2025-04-03 10:34:29','2','Black','FOX-Home','Tel-Aviv',NULL,'הזמנה חדשה'),(45,12,'guy','22','scarlet',1,11.99,'2025-04-03 10:38:30','2','Black','FOX-Home','Tel-Aviv',NULL,'הזמנה חדשה'),(46,14,'amir','22','scarlet',1,11.99,'2025-04-03 11:56:08','Black','Medium','FOX-Home','Tel-Aviv',NULL,'הזמנה חדשה'),(47,15,'sari','22','scarlet',6,71.94,'2025-04-03 12:07:46','Black','Medium','FOX-Home','Tel-Aviv',NULL,'הזמנה חדשה'),(48,8,'shakata','22','scarlet',2,23.98,'2025-04-03 12:12:59','Black','Medium','FOX-Home','Tel-Aviv',NULL,'הזמנה חדשה'),(49,3,'sdv','22','scarlet',1,11.99,'2025-04-03 12:15:20','Black','Medium','FOX-Home','Tel-Aviv',NULL,'הזמנה חדשה'),(50,12,'guy','22','scarlet',2,23.98,'2025-04-03 12:16:40','Black','Medium','FOX-Home','Tel-Aviv',NULL,'הזמנה חדשה'),(51,12,'guy','22','scarlet',1,11.99,'2025-04-03 12:20:27','Black','Medium','FOX-Home','Tel-Aviv',NULL,'הזמנה חדשה'),(52,12,'guy','22','scarlet',1,11.99,'2025-04-03 12:23:04','Black','Medium','FOX-Home','Tel-Aviv',NULL,'הזמנה חדשה'),(53,12,'guy','111','ewrr',72,1799.28,'2025-04-04 12:16:43','Red','M','FOX-Home','Tel-Aviv',NULL,'הזמנה חדשה'),(54,12,'guy','535','shirts',50,2250.00,'2025-04-04 16:19:40',NULL,NULL,'FOX-Home','Tel-Aviv',NULL,'הזמנה חדשה'),(55,12,'guy','12','fox racing',2,19.98,'2025-04-05 08:15:38','yellow','M,L','FOX','Haifa',NULL,'הזמנה חדשה'),(56,12,'guy','12','fox racing',4,39.96,'2025-04-05 10:59:05','yellow','M,L','FOX','Haifa',NULL,'הזמנה חדשה'),(57,12,'guy','535','shirts',45,2025.00,'2025-04-07 07:41:03','Red','XL,M','FOX-Home','Tel-Aviv',NULL,'הזמנה חדשה'),(58,12,'guy','22','scarlet',119,1426.81,'2025-04-07 07:41:54','Black','M','FOX-Home','Tel-Aviv',NULL,'הזמנה חדשה'),(59,8,'shakata','12','fox racing',90,899.10,'2025-04-07 07:42:50','yellow','M,L','FOX','Haifa',NULL,'הזמנה חדשה'),(60,15,'sari','34','reg',10,3450.00,'2025-04-07 08:03:14','Yellow','L','FOX','Haifa',NULL,'הזמנה חדשה'),(61,14,'amir','111','ewrr',10,249.90,'2025-04-07 08:06:15','Red','M','FOX-Home','Tel-Aviv',NULL,'הזמנה חדשה'),(62,15,'sari','2','jeans',11,549.89,'2025-04-07 10:48:22','Blue','L','FOX','Haifa',NULL,'הזמנה חדשה'),(63,12,'guy','22','scarlet',2,23.98,'2025-04-09 08:13:34','Black','M','FOX-Home','Tel-Aviv',NULL,'הזמנה חדשה'),(64,12,'guy','2','jeans',2,99.98,'2025-04-09 08:13:34','Blue','L','FOX','Haifa',NULL,'הזמנה חדשה'),(65,12,'guy','12','fox racing',2,19.98,'2025-04-09 08:13:34','yellow','M,L','FOX','Haifa',NULL,'הזמנה חדשה'),(66,14,'amir','34','reg',2,690.00,'2025-04-09 08:18:58','Yellow','L','FOX','Haifa',NULL,'הזמנה חדשה'),(67,14,'amir','2352','herhe',5,1779.95,'2025-04-09 08:18:58','Red','M','FOX-Home','Tel-Aviv',NULL,'הזמנה חדשה'),(68,14,'amir','221','shirt',3,59.97,'2025-04-09 08:18:58','Black','XL','FOX','Haifa',NULL,'הזמנה חדשה'),(69,14,'amir','12','fox racing',4,39.96,'2025-04-09 08:41:15','yellow','M,L','FOX','Haifa',NULL,'הזמנה חדשה'),(70,14,'amir','111','ewrr',10,249.90,'2025-04-09 08:41:15','Red','M','FOX-Home','Tel-Aviv',NULL,'הזמנה חדשה'),(71,14,'amir','221','shirt',13,259.87,'2025-04-09 08:41:15','Black','XL','FOX','Haifa',NULL,'הזמנה חדשה'),(72,15,'sari','12','fox racing',5,49.95,'2025-04-09 10:16:00','yellow','M,L','FOX','Haifa',NULL,'הזמנה חדשה'),(73,15,'sari','2352','herhe',3,1067.97,'2025-04-09 10:16:00','Red','M','FOX-Home','Tel-Aviv',NULL,'הזמנה חדשה'),(74,13,'marah','1','sdv',6,2075.94,'2025-04-09 11:00:48','Blue','XL','FOX','Haifa',NULL,'הזמנה חדשה'),(75,13,'marah','3','gvs',4,1300.00,'2025-04-09 11:00:48','Red','L','FOX','Haifa',NULL,'הזמנה חדשה'),(76,13,'marah','42','shorts',2,89.98,'2025-04-09 11:00:48','Black','S','FOX','Haifa',NULL,'הזמנה חדשה'),(77,13,'marah','111','ewrr',5,124.95,'2025-04-09 11:00:48','Red','M','FOX-Home','Tel-Aviv',NULL,'הזמנה חדשה'),(78,13,'marah','22','scarlet',1,11.99,'2025-04-09 16:06:42','Black','M','FOX-Home','Tel-Aviv',NULL,'הזמנה חדשה'),(79,13,'marah','2','jeans',1,49.99,'2025-04-09 16:09:03','Blue','L','FOX','Haifa',NULL,'הזמנה חדשה'),(80,13,'marah','2352','herhe',2,711.98,'2025-04-09 16:09:03','Red','M','FOX-Home','Tel-Aviv',NULL,'הזמנה חדשה'),(81,13,'marah','111','ewrr',2,49.98,'2025-04-09 16:09:03','Red','M','FOX-Home','Tel-Aviv',NULL,'הזמנה חדשה'),(82,14,'amir','3','gvs',12,3900.00,'2025-04-12 09:08:54','Red','L','FOX','Haifa',NULL,'הזמנה חדשה'),(83,14,'amir','2','jeans',2,99.98,'2025-04-12 09:08:54','Blue','L','FOX','Haifa',NULL,'הזמנה חדשה'),(84,14,'amir','1','sdv',1,345.99,'2025-04-12 09:08:54','Blue','XL','FOX','Haifa',NULL,'הזמנה חדשה'),(85,11,'sdgsg','111','ewrr',3,74.97,'2025-04-12 16:00:21','Red','M','FOX-Home','Tel-Aviv',NULL,'הזמנה חדשה'),(86,11,'sdgsg','2121','sdsd',12,264.00,'2025-04-12 16:00:21','yellow','S','FOX','Haifa',NULL,'הזמנה חדשה'),(87,11,'sdgsg','3','gvs',6,1950.00,'2025-04-12 16:00:21','Red','L','FOX','Haifa',NULL,'הזמנה חדשה'),(88,11,'sdgsg','111','ewrr',65,1624.35,'2025-04-12 16:01:44','Red','M','FOX-Home','Tel-Aviv',NULL,'הזמנה חדשה'),(89,11,'sdgsg','42','shorts',40,1799.60,'2025-04-12 16:01:44','Black','S','FOX','Haifa',NULL,'הזמנה חדשה'),(90,15,'sari','1','sdv',6,2075.94,'2025-04-13 14:18:01','Blue','XL','FOX','Haifa',NULL,'הזמנה חדשה'),(91,15,'sari','2352','herhe',2,711.98,'2025-04-13 14:18:01','Red','M','FOX-Home','Tel-Aviv',NULL,'הזמנה חדשה'),(92,8,'shakata','1','sdv',4,1383.96,'2025-04-13 16:42:53','Blue','XL','FOX','Haifa',NULL,'הזמנה חדשה'),(93,8,'shakata','221','shirt',2,39.98,'2025-04-13 16:42:53','Black','XL','FOX','Haifa',NULL,'הזמנה חדשה'),(94,8,'shakata','12','fox racing',13,129.87,'2025-04-15 15:59:40','yellow','M,L','FOX','Haifa',NULL,'הזמנה חדשה'),(95,14,'amir','42','shorts',13,584.87,'2025-04-16 08:40:58','Black','S','FOX','Haifa',NULL,'הזמנה חדשה'),(96,15,'sari','2','jeans',10,499.90,'2025-04-20 06:11:07','Blue','L','FOX','Haifa',NULL,'הזמנה חדשה'),(97,15,'sari','12','fox racing',2,19.98,'2025-04-20 06:11:07','yellow','M,L','FOX','Haifa',NULL,'הזמנה חדשה'),(98,15,'sari','22','scarlet',11,131.89,'2025-04-22 17:19:18','Black','M','FOX-Home','Tel-Aviv',NULL,'הזמנה חדשה'),(99,15,'sari','253','wbre',6,2004.00,'2025-03-19 22:00:00','gvew','m','FOX-Home','Tel-Aviv',NULL,'הזמנה חדשה'),(100,16,'afsw','2','jeans',2,99.98,'2025-04-29 08:29:10','Blue','L','FOX','Haifa',NULL,'הזמנה חדשה'),(101,16,'afsw','42','shorts',5,224.95,'2025-04-29 08:29:10','Black','S','FOX','Haifa',NULL,'הזמנה חדשה'),(102,17,NULL,'2',NULL,3,5.97,'2025-05-04 16:41:50',NULL,NULL,NULL,NULL,NULL,'הזמנה חדשה'),(103,15,'sari','2121','sdsd',500,10560.00,'2025-05-10 06:50:59','yellow','S','FOX','Haifa',NULL,'הזמנה חדשה'),(104,15,'sari','22','Scarlet',1,11.99,'2025-05-15 09:16:09','Black','M','FOX-Home','Tel-Aviv',2,'הזמנה חדשה'),(105,16,'afsw','22','Scarlet',1,11.99,'2025-05-15 09:38:00','Black','M','FOX-Home','Tel-Aviv',2,'הזמנה חדשה'),(106,17,'tafa','12','fox racing',2,110.90,'2025-05-22 09:01:07','yellow','M','FOX','Haifa',1,'הזמנה חדשה'),(107,17,'tafa','1','sdv',1,365.98,'2025-05-22 09:04:18','Blue','XL','FOX','Haifa',1,'הזמנה חדשה'),(108,19,NULL,'22','scarlet',1,11.99,'2025-05-22 13:47:04',NULL,NULL,NULL,NULL,NULL,'הזמנה חדשה'),(109,19,NULL,'22','scarlet',1,11.99,'2025-05-22 13:47:08',NULL,NULL,NULL,NULL,NULL,'הזמנה חדשה'),(110,19,'ahmad mostafa shalata','2','jeans',2,99.98,'2025-05-25 16:54:52','Blue','L','FOX','Haifa',1,'סיום המכלה'),(111,15,'sari','2','jeans',2,99.98,'2025-05-27 17:02:31','Blue','L','FOX','Haifa',1,'אישור המכלה');
/*!40000 ALTER TABLE `purchases` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-13 21:53:09
