-- MySQL dump 10.13  Distrib 8.0.34, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: inventory_system
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
  PRIMARY KEY (`customer_id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customers`
--

LOCK TABLES `customers` WRITE;
/*!40000 ALTER TABLE `customers` DISABLE KEYS */;
INSERT INTO `customers` VALUES (1,'dfdh','dhf','dhf'),(2,'sdfh','346','rhe'),(3,'sdv','235','weg'),(4,'shfdf','346','ryhs'),(5,'dfs','235','dsgd'),(6,'sdg','5325','sgddsg'),(7,'ahmad','34634467','dfndrn'),(8,'shakata','32626','egherh'),(9,'dfs','235','dsgd'),(10,'ahmad','52453','gsrwe@gmail.com'),(11,'sdgsg','055883468','fjgxg@gmail.com'),(12,'guy','658568','ehs@gsdg'),(13,'marah','0648458448','marah43y@gmail.com'),(14,'amir','05666481','rhjre34@gmail.com'),(15,'sari','735377205','dfjej@gmail.com');
/*!40000 ALTER TABLE `customers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory`
--

DROP TABLE IF EXISTS `inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inventory` (
  `sku` int NOT NULL AUTO_INCREMENT,
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
  PRIMARY KEY (`sku`),
  KEY `fk_inventory_branch` (`branch_id`),
  CONSTRAINT `fk_inventory_branch` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`branch_id`),
  CONSTRAINT `inventory_ibfk_1` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`branch_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=32526 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory`
--

LOCK TABLES `inventory` WRITE;
/*!40000 ALTER TABLE `inventory` DISABLE KEYS */;
INSERT INTO `inventory` VALUES (1,'sdv','sdbwb',5,345.99,1,'C:/Users/admin/OneDrive/תמונות/צילומי מסך/צילום מסך 2023-05-01 223710.png','Blue','XL',1,2,'2025-04-12 12:08:54'),(2,'Jeans','Clothing',4,49.99,1,'C:/Users/admin/OneDrive/תמונות/צילומי מסך/צילום מסך 2024-02-10 220912.png','Blue','L',2,6,'2025-04-12 12:08:54'),(3,'gvs','wegw',2377,325.00,1,'C:/Users/admin/OneDrive/תמונות/צילומי מסך/צילום מסך 2024-07-30 191917.png','Red','L',2,1,'2025-04-12 12:08:54'),(12,'fox racing','LongShirt',3,9.99,1,'images\\shirt_yellow.jpg','yellow','M,L',1,4,'2025-04-09 13:16:00'),(22,'Scarlet','short',0,11.99,2,'images\\f1348a64acc52399d77572d75e526d047a29eab9_original.jpeg','Black','M',2,5,'2025-04-09 19:06:42'),(34,'reg','erg',2,345.00,1,'images\\shorrt.jpg','Yellow','L',3,5,'2025-04-09 11:18:58'),(42,'shorts','short',48,44.99,1,'C:/Users/admin/OneDrive/שולחן העבודה/פרויקט גמר/InventoryManagementSystem/images/Shorts.jpg','Black','S',4,7,'2025-04-09 14:00:48'),(111,'ewrr','cloths',73,24.99,2,'C:/Users/admin/OneDrive/שולחן העבודה/פרויקט גמר/InventoryManagementSystem/images/Shorts.jpg','Red','M',7,3,'2025-04-09 19:09:03'),(221,'shirt','short',537,19.99,1,'C:/Users/admin/OneDrive/שולחן העבודה/images.jpeg','Black','XL',1,1,'2025-04-09 11:41:15'),(235,'weg','sgdvds',264,235.00,1,NULL,NULL,NULL,NULL,NULL,'2025-04-04 14:55:59'),(535,'shirts','short',5,45.00,2,'C:/Users/admin/OneDrive/תמונות/צילומי מסך/צילום מסך 2024-07-30 191917.png','Red','XL,M',5,3,'2025-04-07 10:41:03'),(2121,'sdsd','cloths',4217,22.00,1,'C:/Users/admin/OneDrive/תמונות/צילומי מסך/צילום מסך 2024-01-21 123124.png','yellow','S',2,1,'2025-04-04 14:59:20'),(2352,'herhe','jnrtj',5,355.99,2,'C:/Users/admin/OneDrive/תמונות/צילומי מסך/צילום מסך 2024-01-21 123124.png','Red','M',3,6,'2025-04-09 19:09:03'),(32525,'asdadas','egwsv',235,25.00,1,NULL,NULL,NULL,NULL,NULL,'2025-04-04 14:55:59');
/*!40000 ALTER TABLE `inventory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `purchases`
--

DROP TABLE IF EXISTS `purchases`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `purchases` (
  `customer_id` int DEFAULT NULL,
  `customer_name` varchar(255) DEFAULT NULL,
  `sku` int DEFAULT NULL,
  `item_name` varchar(255) DEFAULT NULL,
  `quantity` int NOT NULL,
  `total_price` decimal(10,2) NOT NULL,
  `purchase_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `color` varchar(50) DEFAULT NULL,
  `size` varchar(50) DEFAULT NULL,
  `branch_name` varchar(255) DEFAULT NULL,
  `branch_address` varchar(255) DEFAULT NULL,
  `branch_id` int DEFAULT NULL,
  KEY `item_id` (`item_name`),
  KEY `branch_id` (`branch_name`),
  KEY `fk_purchases_customer` (`customer_id`),
  KEY `fk_purchases_sku` (`sku`),
  KEY `fk_purchases_branch` (`branch_id`),
  CONSTRAINT `fk_branch` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`branch_id`),
  CONSTRAINT `fk_customer` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`),
  CONSTRAINT `fk_customers` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`),
  CONSTRAINT `fk_purchases_branch` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`branch_id`),
  CONSTRAINT `fk_purchases_customer` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`),
  CONSTRAINT `fk_purchases_sku` FOREIGN KEY (`sku`) REFERENCES `inventory` (`sku`),
  CONSTRAINT `fk_sku` FOREIGN KEY (`sku`) REFERENCES `inventory` (`sku`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purchases`
--

LOCK TABLES `purchases` WRITE;
/*!40000 ALTER TABLE `purchases` DISABLE KEYS */;
INSERT INTO `purchases` VALUES (7,'ahmad',1,'sdv',1,345.99,'2025-03-16 21:48:57',NULL,NULL,'2',NULL,NULL),(7,'ahmad',1,'sdv',22,7611.78,'2025-03-16 21:57:11',NULL,NULL,'2',NULL,NULL),(8,'shakata',2,'jeans',1,49.99,'2025-03-16 21:57:21',NULL,NULL,'1',NULL,NULL),(7,'ahmad',2,'jeans',2,99.98,'2025-03-16 22:59:37',NULL,NULL,'1',NULL,NULL),(5,'dfs',2352,'herhe',24,8543.76,'2025-03-17 21:26:01',NULL,NULL,'2',NULL,NULL),(7,'ahmad',235,'weg',12,2820.00,'2025-03-18 18:11:52',NULL,NULL,'1',NULL,NULL),(7,'ahmad',1,'sdv',33,11417.67,'2025-03-18 18:29:45',NULL,NULL,'2',NULL,NULL),(5,'dfs',NULL,'hher',22,7612.00,'2025-03-18 18:31:51',NULL,NULL,'FOX',NULL,NULL),(7,'ahmad',2121,'sdsd',11,242.00,'2025-03-18 19:27:04',NULL,NULL,'1',NULL,NULL),(8,'shakata',2121,'sdsd',13,286.00,'2025-03-18 19:27:56',NULL,NULL,'1',NULL,NULL),(7,'ahmad',1,'sdv',11,3805.89,'2025-03-18 19:29:04',NULL,NULL,'2',NULL,NULL),(7,'ahmad',111,'ewrr',22,549.78,'2025-03-18 21:37:52',NULL,NULL,'FOX-Home',NULL,NULL),(7,'ahmad',NULL,'vwnvo',222,5103.78,'2025-03-18 21:55:40',NULL,NULL,'FOX',NULL,NULL),(NULL,NULL,1,'sdv',11,3805.89,'2025-03-18 22:12:39',NULL,NULL,'FOX',NULL,NULL),(NULL,NULL,1,'sdv',122,42210.78,'2025-03-18 22:13:40',NULL,NULL,'FOX',NULL,NULL),(11,'sdgsg',235,'weg',23,5405.00,'2025-03-18 23:04:43',NULL,NULL,'2',NULL,NULL),(NULL,'ahmads',1,'sdv',22,7611.78,'2025-03-18 23:50:06',NULL,NULL,'2',NULL,NULL),(NULL,'rerg',235,'weg',23,5405.00,'2025-03-18 23:51:05',NULL,NULL,'1',NULL,NULL),(7,'ahmad',1,'sdv',23,7957.77,'2025-03-19 00:10:37',NULL,NULL,'FOX-Home',NULL,NULL),(NULL,'aboo',3,'gvs',21,6825.00,'2025-03-19 22:20:42',NULL,NULL,'FOX',NULL,NULL),(NULL,'rfgb',1,'sdv',3,1037.97,'2025-03-19 23:35:40',NULL,NULL,'FOX-Home',NULL,NULL),(NULL,'1',1,'sdv',1,345.99,'2025-03-19 23:38:29',NULL,NULL,'FOX-Home',NULL,NULL),(7,'ahmad',1,'sdv',1,345.99,'2025-03-20 18:50:48',NULL,NULL,'FOX-Home',NULL,NULL),(NULL,'ahmed',235,'weg',2,470.00,'2025-03-20 21:22:46',NULL,NULL,'FOX',NULL,NULL),(NULL,'ahmed',1,'sdv',2,691.98,'2025-03-20 21:23:34',NULL,NULL,'FOX-Home',NULL,NULL),(NULL,'ahmed',235,'weg',1,235.00,'2025-03-20 21:27:59',NULL,NULL,'FOX',NULL,NULL),(NULL,'ahreh',NULL,'hher',1,346.00,'2025-03-20 21:28:56',NULL,NULL,'FOX',NULL,NULL),(7,'ahmad',42,'fsaf',1,43.00,'2025-03-22 19:34:19',NULL,NULL,'FOX',NULL,NULL),(12,'guy',1,'sdv',1,345.99,'2025-03-22 21:07:49',NULL,NULL,'FOX-Home',NULL,NULL),(12,'guy',1,'sdv',3,1037.97,'2025-03-22 21:11:24',NULL,NULL,'FOX-Home',NULL,NULL),(7,'ahmad',1,'sdv',3,1037.97,'2025-03-22 21:11:55',NULL,NULL,'FOX-Home',NULL,NULL),(8,'shakata',2,'jeans',2,99.98,'2025-03-22 21:14:59',NULL,NULL,'FOX',NULL,NULL),(8,'shakata',1,'sdv',1,345.99,'2025-03-22 21:40:03',NULL,NULL,'FOX-Home','Tel-Aviv',NULL),(3,'sdv',3,'gvs',120,39000.00,'2025-03-22 22:08:01',NULL,NULL,'FOX','Haifa',NULL),(1,'dfdh',42,'fsaf',5,215.00,'2025-03-22 22:09:10',NULL,NULL,'FOX','Haifa',NULL),(3,'sdv',34,'reg',33,11385.00,'2025-03-22 23:12:07',NULL,NULL,'FOX','Haifa',NULL),(8,'shakata',NULL,'vwnvo',10,229.90,'2025-03-24 20:19:51',NULL,NULL,'FOX','Haifa',NULL),(11,'sdgsg',34,'reg',22,7590.00,'2025-03-24 22:07:44',NULL,NULL,'FOX','Haifa',NULL),(8,'shakata',34,'reg',10,3450.00,'2025-03-29 19:50:22',NULL,NULL,'FOX','Haifa',NULL),(8,'shakata',221,'shirt',11,219.89,'2025-03-29 20:06:44',NULL,NULL,'FOX','Haifa',NULL),(8,'shakata',22,'Scarlet',5,59.95,'2025-04-02 09:47:58',NULL,NULL,'FOX-Home','Tel-Aviv',NULL),(12,'guy',22,'scarlet',1,11.99,'2025-04-03 08:57:12','2','Black','FOX-Home','Tel-Aviv',NULL),(14,'amir',22,'scarlet',3,35.97,'2025-04-03 10:29:38','2','Black','FOX-Home','Tel-Aviv',NULL),(11,'sdgsg',22,'scarlet',2,23.98,'2025-04-03 10:34:29','2','Black','FOX-Home','Tel-Aviv',NULL),(12,'guy',22,'scarlet',1,11.99,'2025-04-03 10:38:30','2','Black','FOX-Home','Tel-Aviv',NULL),(14,'amir',22,'scarlet',1,11.99,'2025-04-03 11:56:08','Black','Medium','FOX-Home','Tel-Aviv',NULL),(15,'sari',22,'scarlet',6,71.94,'2025-04-03 12:07:46','Black','Medium','FOX-Home','Tel-Aviv',NULL),(8,'shakata',22,'scarlet',2,23.98,'2025-04-03 12:12:59','Black','Medium','FOX-Home','Tel-Aviv',NULL),(3,'sdv',22,'scarlet',1,11.99,'2025-04-03 12:15:20','Black','Medium','FOX-Home','Tel-Aviv',NULL),(12,'guy',22,'scarlet',2,23.98,'2025-04-03 12:16:40','Black','Medium','FOX-Home','Tel-Aviv',NULL),(12,'guy',22,'scarlet',1,11.99,'2025-04-03 12:20:27','Black','Medium','FOX-Home','Tel-Aviv',NULL),(12,'guy',22,'scarlet',1,11.99,'2025-04-03 12:23:04','Black','Medium','FOX-Home','Tel-Aviv',NULL),(12,'guy',111,'ewrr',72,1799.28,'2025-04-04 12:16:43','Red','M','FOX-Home','Tel-Aviv',NULL),(12,'guy',535,'shirts',50,2250.00,'2025-04-04 16:19:40',NULL,NULL,'FOX-Home','Tel-Aviv',NULL),(12,'guy',12,'fox racing',2,19.98,'2025-04-05 08:15:38','yellow','M,L','FOX','Haifa',NULL),(12,'guy',12,'fox racing',4,39.96,'2025-04-05 10:59:05','yellow','M,L','FOX','Haifa',NULL),(12,'guy',535,'shirts',45,2025.00,'2025-04-07 07:41:03','Red','XL,M','FOX-Home','Tel-Aviv',NULL),(12,'guy',22,'scarlet',119,1426.81,'2025-04-07 07:41:54','Black','M','FOX-Home','Tel-Aviv',NULL),(8,'shakata',12,'fox racing',90,899.10,'2025-04-07 07:42:50','yellow','M,L','FOX','Haifa',NULL),(15,'sari',34,'reg',10,3450.00,'2025-04-07 08:03:14','Yellow','L','FOX','Haifa',NULL),(14,'amir',111,'ewrr',10,249.90,'2025-04-07 08:06:15','Red','M','FOX-Home','Tel-Aviv',NULL),(15,'sari',2,'jeans',11,549.89,'2025-04-07 10:48:22','Blue','L','FOX','Haifa',NULL),(12,'guy',22,'scarlet',2,23.98,'2025-04-09 08:13:34','Black','M','FOX-Home','Tel-Aviv',NULL),(12,'guy',2,'jeans',2,99.98,'2025-04-09 08:13:34','Blue','L','FOX','Haifa',NULL),(12,'guy',12,'fox racing',2,19.98,'2025-04-09 08:13:34','yellow','M,L','FOX','Haifa',NULL),(14,'amir',34,'reg',2,690.00,'2025-04-09 08:18:58','Yellow','L','FOX','Haifa',NULL),(14,'amir',2352,'herhe',5,1779.95,'2025-04-09 08:18:58','Red','M','FOX-Home','Tel-Aviv',NULL),(14,'amir',221,'shirt',3,59.97,'2025-04-09 08:18:58','Black','XL','FOX','Haifa',NULL),(14,'amir',12,'fox racing',4,39.96,'2025-04-09 08:41:15','yellow','M,L','FOX','Haifa',NULL),(14,'amir',111,'ewrr',10,249.90,'2025-04-09 08:41:15','Red','M','FOX-Home','Tel-Aviv',NULL),(14,'amir',221,'shirt',13,259.87,'2025-04-09 08:41:15','Black','XL','FOX','Haifa',NULL),(15,'sari',12,'fox racing',5,49.95,'2025-04-09 10:16:00','yellow','M,L','FOX','Haifa',NULL),(15,'sari',2352,'herhe',3,1067.97,'2025-04-09 10:16:00','Red','M','FOX-Home','Tel-Aviv',NULL),(13,'marah',1,'sdv',6,2075.94,'2025-04-09 11:00:48','Blue','XL','FOX','Haifa',NULL),(13,'marah',3,'gvs',4,1300.00,'2025-04-09 11:00:48','Red','L','FOX','Haifa',NULL),(13,'marah',42,'shorts',2,89.98,'2025-04-09 11:00:48','Black','S','FOX','Haifa',NULL),(13,'marah',111,'ewrr',5,124.95,'2025-04-09 11:00:48','Red','M','FOX-Home','Tel-Aviv',NULL),(13,'marah',22,'scarlet',1,11.99,'2025-04-09 16:06:42','Black','M','FOX-Home','Tel-Aviv',NULL),(13,'marah',2,'jeans',1,49.99,'2025-04-09 16:09:03','Blue','L','FOX','Haifa',NULL),(13,'marah',2352,'herhe',2,711.98,'2025-04-09 16:09:03','Red','M','FOX-Home','Tel-Aviv',NULL),(13,'marah',111,'ewrr',2,49.98,'2025-04-09 16:09:03','Red','M','FOX-Home','Tel-Aviv',NULL),(14,'amir',3,'gvs',12,3900.00,'2025-04-12 09:08:54','Red','L','FOX','Haifa',NULL),(14,'amir',2,'jeans',2,99.98,'2025-04-12 09:08:54','Blue','L','FOX','Haifa',NULL),(14,'amir',1,'sdv',1,345.99,'2025-04-12 09:08:54','Blue','XL','FOX','Haifa',NULL);
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

-- Dump completed on 2025-04-12 16:11:37
