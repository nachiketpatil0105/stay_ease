-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: stayease
-- ------------------------------------------------------
-- Server version	8.0.41

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
-- Dumping data for table `complaint_types`
--

LOCK TABLES `complaint_types` WRITE;
/*!40000 ALTER TABLE `complaint_types` DISABLE KEYS */;
INSERT INTO `complaint_types` VALUES (1,'Plumbing','Water Leakage'),(2,'Electrical','Fan/Light Not Working'),(3,'Civil','Broken Window'),(4,'IT','Wi-Fi Issue');
/*!40000 ALTER TABLE `complaint_types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `complaints`
--

LOCK TABLES `complaints` WRITE;
/*!40000 ALTER TABLE `complaints` DISABLE KEYS */;
INSERT INTO `complaints` VALUES (1,110,1,'Tap in bathroom is leaking constantly.','2026-03-15',NULL,'Pending'),(2,111,4,'Wi-Fi keeps dropping in room 202.','2026-03-10','2026-03-11','Resolved'),(3,112,2,'Ceiling fan makes a loud noise.','2026-03-17',NULL,'Pending');
/*!40000 ALTER TABLE `complaints` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `fee_structures`
--

LOCK TABLES `fee_structures` WRITE;
/*!40000 ALTER TABLE `fee_structures` DISABLE KEYS */;
INSERT INTO `fee_structures` VALUES (1,'Semester Hostel Rent',25000.00,'2025-2026'),(2,'Gym Membership',2000.00,'2025-2026');
/*!40000 ALTER TABLE `fee_structures` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `furniture_inventory`
--

LOCK TABLES `furniture_inventory` WRITE;
/*!40000 ALTER TABLE `furniture_inventory` DISABLE KEYS */;
INSERT INTO `furniture_inventory` VALUES (1,'Single Bed',201,'2023-05-10','Good'),(2,'Study Table',201,'2023-05-10','Damaged'),(3,'Single Bed',202,'2023-05-10','Good'),(4,'Study Table',202,'2023-05-10','Good'),(5,'Single Bed',101,'2022-08-15','Good'),(6,'Wardrobe',101,'2022-08-15','Good'),(7,'Single Bed',102,'2024-01-20','Good'),(18,'Single Bed',101,'2024-01-15','Good'),(19,'Study Desk',101,'2024-01-15','Good'),(20,'Desk Chair',101,'2024-01-15','Damaged'),(21,'Wardrobe',101,'2024-01-15','Good'),(22,'Single Bed',102,'2024-01-15','Good');
/*!40000 ALTER TABLE `furniture_inventory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `hostels`
--

LOCK TABLES `hostels` WRITE;
/*!40000 ALTER TABLE `hostels` DISABLE KEYS */;
INSERT INTO `hostels` VALUES (1,'Yamuna Hostel','Girls',3,102,120),(2,'Narmada Hostel','Boys',4,106,122),(3,'Ganga Hostel','Boys',5,108,NULL);
/*!40000 ALTER TABLE `hostels` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `member_movement_logs`
--

LOCK TABLES `member_movement_logs` WRITE;
/*!40000 ALTER TABLE `member_movement_logs` DISABLE KEYS */;
INSERT INTO `member_movement_logs` VALUES (1,110,'2026-03-17 03:00:00','2026-03-17 08:30:00','Attending College Lectures'),(2,112,'2026-03-17 12:30:00','2026-03-17 16:00:00','Going to the Gym'),(3,111,'2026-03-18 03:30:00','2026-03-18 08:15:00','Lab Work'),(4,113,'2026-03-18 14:30:00',NULL,'Going home for the weekend'),(8,110,'2025-10-10 12:30:00','2025-10-10 16:00:00','Going to market for groceries'),(9,111,'2025-10-12 08:30:00','2025-10-14 02:30:00','Weekend trip to hometown'),(10,113,'2026-03-21 07:45:37',NULL,'Library study session');
/*!40000 ALTER TABLE `member_movement_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `members`
--

LOCK TABLES `members` WRITE;
/*!40000 ALTER TABLE `members` DISABLE KEYS */;
INSERT INTO `members` VALUES (100,'Super','Admin','M',45,'9999999999','admin@stayease.com','9999999998','uploads/default.png',3,'Active'),(102,'Riya','Patel','F',32,'9876500002','riya@stayease.com','9876500003','uploads/default.png',2,'Active'),(106,'Rakesh','Verma','M',38,'9876500006','rakesh@stayease.com','9876500007','uploads/default.png',2,'Active'),(108,'Vikram','Desai','M',41,'9876500008','vikram@stayease.com','9876500009','uploads/default.png',2,'Active'),(110,'Priya','Sharma','F',20,'8888800001','priya@student.com','7777700001','uploads/default.png',1,'Active'),(111,'Ananya','Gupta','F',19,'8888800002','ananya@student.com','7777700002','uploads/default.png',1,'Active'),(112,'Rahul','Singh','M',21,'8888800003','rahul@student.com','7777700003','uploads/default.png',1,'Active'),(113,'Karan','Kumar','M',20,'8888800004','karan@student.com','7777700004','uploads/default.png',1,'Active'),(114,'Amit','Patel','M',20,'8888800005','amit@student.com','7777700005','uploads/default.png',1,'Active'),(115,'Rohan','Sharma','M',19,'8888800006','rohan@student.com','7777700006','uploads/default.png',1,'Active'),(116,'Neha','Singh','F',21,'8888800007','neha@student.com','7777700007','uploads/default.png',1,'Active'),(117,'Sneha','Reddy','F',20,'8888800008','sneha@student.com','7777700008','uploads/default.png',1,'Active'),(118,'Arjun','Das','M',19,'8888800009','arjun@student.com','7777700009','uploads/default.png',1,'Active'),(119,'Kabir','Khan','M',22,'8888800010','kabir@student.com','7777700010','uploads/default.png',1,'Active'),(120,'Ramesh','Singh','M',45,'9876543210','ramesh.sec@stayease.com',NULL,'uploads/default.png',4,'Active'),(122,'Security','Narmada','M',35,'8987384932','narmada.sec@stayease.com','9876500000','uploads/default.png',4,'Active'),(125,'Aman','Raj','M',25,'8987384933','aman@stayease.com','9876500000','uploads/default.png',4,'Active');
/*!40000 ALTER TABLE `members` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `payments`
--

LOCK TABLES `payments` WRITE;
/*!40000 ALTER TABLE `payments` DISABLE KEYS */;
INSERT INTO `payments` VALUES (1,110,1,'2026-01-05',25000.00,'Success','TXN-998877'),(2,110,2,'2026-01-06',2000.00,'Success','TXN-998878'),(3,112,1,'2026-01-10',25000.00,'Success','TXN-998879');
/*!40000 ALTER TABLE `payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'Student','Regular resident of the hostel'),(2,'Warden','Manages a specific hostel block'),(3,'Admin','Overall system administrator'),(4,'Security','Gate security guard for specific hostels');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `room_allocations`
--

LOCK TABLES `room_allocations` WRITE;
/*!40000 ALTER TABLE `room_allocations` DISABLE KEYS */;
INSERT INTO `room_allocations` VALUES (1,110,201,'2026-01-10',NULL,'Active'),(2,111,202,'2026-01-12',NULL,'Active'),(3,112,101,'2026-01-15',NULL,'Active'),(4,113,102,'2026-01-18',NULL,'Active'),(5,114,301,'2026-02-01',NULL,'Active'),(6,115,301,'2026-02-05',NULL,'Active'),(7,116,201,'2026-02-10',NULL,'Active'),(8,117,202,'2026-02-12',NULL,'Active'),(9,118,302,'2026-02-15',NULL,'Active'),(10,119,101,'2026-02-20',NULL,'Active'),(11,122,102,'2026-03-21',NULL,'Active'),(12,125,302,'2026-03-21',NULL,'Active');
/*!40000 ALTER TABLE `room_allocations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `rooms`
--

LOCK TABLES `rooms` WRITE;
/*!40000 ALTER TABLE `rooms` DISABLE KEYS */;
INSERT INTO `rooms` VALUES (101,'101',2,1,2),(102,'102',2,1,2),(201,'201',1,2,2),(202,'202',1,2,2),(301,'101',3,1,2),(302,'102',3,1,2);
/*!40000 ALTER TABLE `rooms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `user_credentials`
--

LOCK TABLES `user_credentials` WRITE;
/*!40000 ALTER TABLE `user_credentials` DISABLE KEYS */;
INSERT INTO `user_credentials` VALUES (100,'admin','scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9'),(102,'riya','scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9'),(106,'rakesh','scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9'),(108,'vikram','scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9'),(110,'priya','scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9'),(111,'ananya','scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9'),(112,'rahul','scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9'),(113,'karan','scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9'),(114,'amit','scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9'),(115,'rohan','scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9'),(116,'neha','scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9'),(117,'sneha','scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9'),(118,'arjun','scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9'),(119,'kabir','scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9'),(120,'security','scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9'),(122,'security_h1','scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9');
/*!40000 ALTER TABLE `user_credentials` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `visitor_logs`
--

LOCK TABLES `visitor_logs` WRITE;
/*!40000 ALTER TABLE `visitor_logs` DISABLE KEYS */;
INSERT INTO `visitor_logs` VALUES (1,'Ramesh Sharma','9876543210','Aadhar Card','1234-5678-9012',110,'2026-03-15 04:30:00',NULL,'Visiting daughter'),(2,'Suresh Singh','8765432109','Driving License','DL-9876543',112,'2026-03-16 11:00:00',NULL,'Delivering books'),(3,'Neha Gupta','7654321098','College ID','STU-2025-001',111,'2026-03-18 05:45:00',NULL,'Group Study'),(4,'Anita Sharma','9988776655','Aadhar','1234-5678-9012',110,'2025-09-01 04:30:00','2025-09-01 08:30:00','Parent visiting'),(5,'Rahul Verma','8877665544','Driving License','DL-98765',111,'2026-03-21 08:45:37',NULL,'Project discussion');
/*!40000 ALTER TABLE `visitor_logs` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-21 18:40:38
