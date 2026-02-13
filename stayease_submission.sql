-- MySQL dump 10.13  Distrib 8.0.45, for Linux (x86_64)
--
-- Host: localhost    Database: stayease
-- ------------------------------------------------------
-- Server version	8.0.45-0ubuntu0.22.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Complaint_Types`
--

DROP TABLE IF EXISTS `Complaint_Types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Complaint_Types` (
  `Complaint_Type_ID` int NOT NULL,
  `Type_Name` varchar(100) NOT NULL,
  `Sub_Type` varchar(100) NOT NULL,
  PRIMARY KEY (`Complaint_Type_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Complaint_Types`
--

LOCK TABLES `Complaint_Types` WRITE;
/*!40000 ALTER TABLE `Complaint_Types` DISABLE KEYS */;
INSERT INTO `Complaint_Types` VALUES (901,'Electrical','Fan'),(902,'Electrical','Switch'),(903,'Electrical','Light'),(904,'Plumbing','Tap'),(905,'Plumbing','Toilet'),(906,'Civil','Wall Crack'),(907,'Civil','Door Lock'),(908,'Mechanical','Bed Frame'),(909,'Mechanical','Window'),(910,'Other','General Cleaning');
/*!40000 ALTER TABLE `Complaint_Types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Complaints`
--

DROP TABLE IF EXISTS `Complaints`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Complaints` (
  `Complaint_ID` int NOT NULL,
  `Member_ID` int NOT NULL,
  `Complaint_Type_ID` int NOT NULL,
  `Description` text NOT NULL,
  `Submission_Date` date NOT NULL,
  `Resolved_Date` date DEFAULT NULL,
  `Status` varchar(20) NOT NULL,
  PRIMARY KEY (`Complaint_ID`),
  KEY `fk_complaint_member` (`Member_ID`),
  KEY `fk_complaint_type` (`Complaint_Type_ID`),
  CONSTRAINT `fk_complaint_member` FOREIGN KEY (`Member_ID`) REFERENCES `Members` (`Member_ID`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_complaint_type` FOREIGN KEY (`Complaint_Type_ID`) REFERENCES `Complaint_Types` (`Complaint_Type_ID`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `chk_resolution_logic` CHECK ((((`Status` = _utf8mb4'Resolved') and (`Resolved_Date` is not null)) or (`Status` in (_utf8mb4'Pending',_utf8mb4'In Progress')))),
  CONSTRAINT `Complaints_chk_1` CHECK ((`Status` in (_utf8mb4'Pending',_utf8mb4'In Progress',_utf8mb4'Resolved')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Complaints`
--

LOCK TABLES `Complaints` WRITE;
/*!40000 ALTER TABLE `Complaints` DISABLE KEYS */;
INSERT INTO `Complaints` VALUES (1001,101,901,'Fan not working properly','2025-01-10','2025-01-12','Resolved'),(1002,102,904,'Water leakage from tap','2025-01-11',NULL,'Pending'),(1003,103,906,'Crack in wall near window','2025-01-12','2025-01-15','Resolved'),(1004,104,907,'Door lock broken','2025-01-13',NULL,'In Progress'),(1005,101,903,'Light flickering frequently','2025-01-14','2025-01-16','Resolved'),(1006,102,905,'Toilet flush not working','2025-01-15',NULL,'Pending'),(1007,103,908,'Bed frame loose','2025-01-16','2025-01-18','Resolved'),(1008,104,909,'Window hinge broken','2025-01-17',NULL,'In Progress'),(1009,101,902,'Switch malfunctioning','2025-01-18','2025-01-19','Resolved'),(1010,102,910,'Room cleaning required','2025-01-19',NULL,'Pending');
/*!40000 ALTER TABLE `Complaints` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Fee_Structures`
--

DROP TABLE IF EXISTS `Fee_Structures`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Fee_Structures` (
  `Fee_Type_ID` int NOT NULL,
  `Fee_Name` varchar(150) NOT NULL,
  `Amount` decimal(10,2) NOT NULL,
  `Academic_Year` varchar(20) NOT NULL,
  PRIMARY KEY (`Fee_Type_ID`),
  CONSTRAINT `Fee_Structures_chk_1` CHECK ((`Amount` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Fee_Structures`
--

LOCK TABLES `Fee_Structures` WRITE;
/*!40000 ALTER TABLE `Fee_Structures` DISABLE KEYS */;
INSERT INTO `Fee_Structures` VALUES (701,'Hostel Rent',45000.00,'2025-2026'),(702,'Mess Rent',30000.00,'2025-2026'),(703,'Laundry Charges',5000.00,'2025-2026'),(704,'Maintenance Fee',8000.00,'2025-2026'),(705,'Electricity Charges',6000.00,'2025-2026'),(706,'Security Deposit',10000.00,'2025-2026'),(707,'Water Charges',4000.00,'2025-2026'),(708,'Internet Fee',3500.00,'2025-2026'),(709,'Gym Fee',2000.00,'2025-2026'),(710,'Library Access Fee',1500.00,'2025-2026');
/*!40000 ALTER TABLE `Fee_Structures` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Furniture_Inventory`
--

DROP TABLE IF EXISTS `Furniture_Inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Furniture_Inventory` (
  `Furniture_ID` int NOT NULL,
  `Item_Name` varchar(100) NOT NULL,
  `Room_ID` int NOT NULL,
  `Purchase_Date` date NOT NULL,
  `Current_Condition` varchar(7) NOT NULL,
  PRIMARY KEY (`Furniture_ID`),
  KEY `fk_furniture_room` (`Room_ID`),
  CONSTRAINT `fk_furniture_room` FOREIGN KEY (`Room_ID`) REFERENCES `Rooms` (`Room_ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `Furniture_Inventory_chk_1` CHECK ((`Current_Condition` in (_utf8mb4'Good',_utf8mb4'Damaged')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Furniture_Inventory`
--

LOCK TABLES `Furniture_Inventory` WRITE;
/*!40000 ALTER TABLE `Furniture_Inventory` DISABLE KEYS */;
INSERT INTO `Furniture_Inventory` VALUES (401,'Bed',201,'2023-06-01','Good'),(402,'Table',201,'2023-06-01','Good'),(403,'Chair',203,'2023-07-01','Good'),(404,'Cupboard',205,'2023-08-01','Damaged'),(405,'Bed',207,'2023-06-01','Good'),(406,'Table',207,'2023-06-01','Good'),(407,'Chair',209,'2023-07-01','Good'),(408,'Fan',210,'2023-08-01','Good'),(409,'Light',202,'2023-05-01','Good'),(410,'Desk',204,'2023-05-01','Damaged');
/*!40000 ALTER TABLE `Furniture_Inventory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Hostels`
--

DROP TABLE IF EXISTS `Hostels`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Hostels` (
  `Hostel_ID` int NOT NULL,
  `Hostel_Name` varchar(150) NOT NULL,
  `Hostel_Type` varchar(5) NOT NULL,
  `Total_Floors` int NOT NULL,
  `Warden_ID` int NOT NULL,
  PRIMARY KEY (`Hostel_ID`),
  UNIQUE KEY `Hostel_Name` (`Hostel_Name`),
  KEY `fk_hostel_warden` (`Warden_ID`),
  CONSTRAINT `fk_hostel_warden` FOREIGN KEY (`Warden_ID`) REFERENCES `Members` (`Member_ID`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `Hostels_chk_1` CHECK ((`Hostel_Type` in (_utf8mb4'Boys',_utf8mb4'Girls'))),
  CONSTRAINT `Hostels_chk_2` CHECK ((`Total_Floors` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Hostels`
--

LOCK TABLES `Hostels` WRITE;
/*!40000 ALTER TABLE `Hostels` DISABLE KEYS */;
INSERT INTO `Hostels` VALUES (1,'Aibaan','Boys',4,106),(2,'Beauki','Girls',5,107),(3,'Chimair','Boys',4,106),(4,'Duven','Girls',5,107),(5,'Emiet','Boys',6,106),(6,'Firpeal','Girls',4,107),(7,'Griwiksh','Boys',5,106),(8,'Hiqom','Girls',4,107),(9,'Ljokha','Boys',3,106),(10,'Jurqia','Girls',5,107),(11,'Kyzeel','Boys',4,106),(12,'Lekhaag','Girls',5,107);
/*!40000 ALTER TABLE `Hostels` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Member_Movement_Logs`
--

DROP TABLE IF EXISTS `Member_Movement_Logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Member_Movement_Logs` (
  `Movement_ID` int NOT NULL,
  `Member_ID` int NOT NULL,
  `Exit_Time` timestamp NOT NULL,
  `Entry_Time` timestamp NULL DEFAULT NULL,
  `Purpose` varchar(255) NOT NULL,
  PRIMARY KEY (`Movement_ID`),
  KEY `fk_movement_member` (`Member_ID`),
  CONSTRAINT `fk_movement_member` FOREIGN KEY (`Member_ID`) REFERENCES `Members` (`Member_ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `chk_movement_time` CHECK (((`Entry_Time` > `Exit_Time`) or (`Entry_Time` is null)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Member_Movement_Logs`
--

LOCK TABLES `Member_Movement_Logs` WRITE;
/*!40000 ALTER TABLE `Member_Movement_Logs` DISABLE KEYS */;
INSERT INTO `Member_Movement_Logs` VALUES (601,101,'2025-02-10 03:00:00','2025-02-10 12:15:00','Classes and lab'),(602,102,'2025-02-10 03:30:00','2025-02-10 12:40:00','Classes and gym'),(603,103,'2025-02-11 03:15:00','2025-02-11 14:00:00','Classes and club activity'),(604,104,'2025-02-11 04:45:00','2025-02-11 11:20:00','Project work'),(605,105,'2025-02-12 03:50:00','2025-02-12 12:35:00','Classes'),(606,101,'2025-02-13 08:30:00','2025-02-13 12:00:00','Library'),(607,102,'2025-02-14 11:30:00','2025-02-14 14:40:00','Sports practice'),(608,103,'2025-02-15 06:00:00','2025-02-15 10:10:00','Academic meeting'),(609,104,'2025-02-16 13:00:00','2025-02-16 15:30:00','Dinner outside'),(610,105,'2025-02-17 02:45:00',NULL,'Classes ongoing');
/*!40000 ALTER TABLE `Member_Movement_Logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Members`
--

DROP TABLE IF EXISTS `Members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Members` (
  `Member_ID` int NOT NULL,
  `First_Name` varchar(100) NOT NULL,
  `Last_Name` varchar(100) DEFAULT NULL,
  `Gender` char(1) NOT NULL,
  `Age` int NOT NULL,
  `Contact_Number` varchar(15) NOT NULL,
  `Email` varchar(150) NOT NULL,
  `Emergency_Contact` varchar(15) DEFAULT NULL,
  `Image_Path` varchar(255) NOT NULL DEFAULT 'uploads/default.png',
  `Role_ID` int NOT NULL,
  `Status` varchar(20) NOT NULL,
  PRIMARY KEY (`Member_ID`),
  UNIQUE KEY `Contact_Number` (`Contact_Number`),
  UNIQUE KEY `Email` (`Email`),
  KEY `fk_member_role` (`Role_ID`),
  CONSTRAINT `fk_member_role` FOREIGN KEY (`Role_ID`) REFERENCES `Roles` (`Role_ID`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `Members_chk_1` CHECK ((`Gender` in (_utf8mb4'M',_utf8mb4'F'))),
  CONSTRAINT `Members_chk_2` CHECK ((`Age` > 0)),
  CONSTRAINT `Members_chk_3` CHECK ((`Status` in (_utf8mb4'Active',_utf8mb4'Inactive')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Members`
--

LOCK TABLES `Members` WRITE;
/*!40000 ALTER TABLE `Members` DISABLE KEYS */;
INSERT INTO `Members` VALUES (101,'Nityanand','Karmali','M',20,'9876501001','nityanand.k@iitgn.ac.in','9876601001','uploads/nityanand.png',1,'Active'),(102,'Niraj','Kumar','M',21,'9876501002','niraj.k@iitgn.ac.in','9876601002','uploads/niraj.png',1,'Active'),(103,'Nachiket','Patil','M',20,'9876501003','nachiket.p@iitgn.ac.in','9876601003','uploads/nachiket.png',1,'Active'),(104,'Parth','Kale','M',22,'9876501004','parth.k@iitgn.ac.in','9876601004','uploads/parth.png',1,'Active'),(105,'Aryan','Kumar','M',19,'9876501005','aryan.k@iitgn.ac.in','9876601005','uploads/aryan.png',1,'Active'),(106,'Drishti','Rao','F',45,'9876501006','drishti.rao@iitgn.ac.in','9876601006','uploads/drishti.png',2,'Active'),(107,'Rakesh','Verma','M',48,'9876501007','rakesh.verma@iitgn.ac.in','9876601007','uploads/rakesh.png',2,'Active'),(108,'Sunil','Kumar','M',36,'9876501008','sunil.k@iitgn.ac.in','9876601008','uploads/sunil.png',3,'Active'),(109,'Arjun','Nair','M',40,'9876501009','arjun.nair@iitgn.ac.in','9876601009','uploads/arjun.png',4,'Active'),(110,'Neha','Joshi','F',30,'9876501010','neha.joshi@iitgn.ac.in','9876601010','uploads/neha.png',5,'Active');
/*!40000 ALTER TABLE `Members` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Payments`
--

DROP TABLE IF EXISTS `Payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Payments` (
  `Payment_ID` int NOT NULL,
  `Member_ID` int NOT NULL,
  `Fee_Type_ID` int NOT NULL,
  `Payment_Date` date NOT NULL,
  `Amount_Paid` decimal(10,2) NOT NULL,
  `Payment_Status` varchar(20) NOT NULL,
  `Transaction_Reference` varchar(100) NOT NULL,
  PRIMARY KEY (`Payment_ID`),
  UNIQUE KEY `Transaction_Reference` (`Transaction_Reference`),
  KEY `fk_payment_member` (`Member_ID`),
  KEY `fk_payment_fee` (`Fee_Type_ID`),
  CONSTRAINT `fk_payment_fee` FOREIGN KEY (`Fee_Type_ID`) REFERENCES `Fee_Structures` (`Fee_Type_ID`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_payment_member` FOREIGN KEY (`Member_ID`) REFERENCES `Members` (`Member_ID`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `Payments_chk_1` CHECK ((`Amount_Paid` > 0)),
  CONSTRAINT `Payments_chk_2` CHECK ((`Payment_Status` in (_utf8mb4'Success',_utf8mb4'Failed')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Payments`
--

LOCK TABLES `Payments` WRITE;
/*!40000 ALTER TABLE `Payments` DISABLE KEYS */;
INSERT INTO `Payments` VALUES (801,101,701,'2025-01-05',45000.00,'Success','TXN1001'),(802,102,702,'2025-01-06',30000.00,'Success','TXN1002'),(803,103,703,'2025-01-07',5000.00,'Success','TXN1003'),(804,104,704,'2025-01-08',8000.00,'Success','TXN1004'),(805,101,705,'2025-01-09',6000.00,'Success','TXN1005'),(806,102,706,'2025-01-10',10000.00,'Success','TXN1006'),(807,103,707,'2025-01-11',4000.00,'Success','TXN1007'),(808,104,708,'2025-01-12',3500.00,'Failed','TXN1008'),(809,101,709,'2025-01-13',2000.00,'Success','TXN1009'),(810,102,710,'2025-01-14',1500.00,'Success','TXN1010');
/*!40000 ALTER TABLE `Payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Roles`
--

DROP TABLE IF EXISTS `Roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Roles` (
  `Role_ID` int NOT NULL,
  `Role_Name` varchar(100) NOT NULL,
  `Description` text NOT NULL,
  PRIMARY KEY (`Role_ID`),
  UNIQUE KEY `Role_Name` (`Role_Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Roles`
--

LOCK TABLES `Roles` WRITE;
/*!40000 ALTER TABLE `Roles` DISABLE KEYS */;
INSERT INTO `Roles` VALUES (1,'Student','Resident student of the hostel'),(2,'Warden','Overall in-charge of hostel management'),(3,'Technician','Handles maintenance and repairs'),(4,'Security','Responsible for entry/exit monitoring'),(5,'Cleaner','Maintains hostel cleanliness'),(6,'MessManager','Handles mess operations'),(7,'Accountant','Manages financial transactions'),(8,'Electrician','Handles electrical issues'),(9,'Plumber','Handles plumbing issues'),(10,'Admin','Administrative staff member');
/*!40000 ALTER TABLE `Roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Room_Allocations`
--

DROP TABLE IF EXISTS `Room_Allocations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Room_Allocations` (
  `Allocation_ID` int NOT NULL,
  `Member_ID` int NOT NULL,
  `Room_ID` int NOT NULL,
  `Allocation_Date` date NOT NULL,
  `Check_Out_Date` date DEFAULT NULL,
  `Status` varchar(20) NOT NULL,
  PRIMARY KEY (`Allocation_ID`),
  KEY `fk_allocation_member` (`Member_ID`),
  KEY `fk_allocation_room` (`Room_ID`),
  CONSTRAINT `fk_allocation_member` FOREIGN KEY (`Member_ID`) REFERENCES `Members` (`Member_ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_allocation_room` FOREIGN KEY (`Room_ID`) REFERENCES `Rooms` (`Room_ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `chk_checkout_date` CHECK (((`Check_Out_Date` > `Allocation_Date`) or (`Check_Out_Date` is null))),
  CONSTRAINT `Room_Allocations_chk_1` CHECK ((`Status` in (_utf8mb4'Active',_utf8mb4'Inactive')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Room_Allocations`
--

LOCK TABLES `Room_Allocations` WRITE;
/*!40000 ALTER TABLE `Room_Allocations` DISABLE KEYS */;
INSERT INTO `Room_Allocations` VALUES (301,101,201,'2025-01-05',NULL,'Active'),(302,102,202,'2025-01-06',NULL,'Active'),(303,103,203,'2025-01-07',NULL,'Active'),(304,104,205,'2025-01-08',NULL,'Active'),(305,105,207,'2025-01-09',NULL,'Active'),(306,101,209,'2024-01-10','2024-12-15','Inactive'),(307,102,210,'2024-01-12','2024-12-10','Inactive'),(308,103,204,'2024-01-15','2024-12-05','Inactive'),(309,104,206,'2024-01-18','2024-11-30','Inactive'),(310,105,208,'2024-01-20','2024-11-25','Inactive');
/*!40000 ALTER TABLE `Room_Allocations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Rooms`
--

DROP TABLE IF EXISTS `Rooms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Rooms` (
  `Room_ID` int NOT NULL,
  `Room_Number` varchar(20) NOT NULL,
  `Hostel_ID` int NOT NULL,
  `Floor_Number` int NOT NULL,
  `Capacity` int NOT NULL,
  PRIMARY KEY (`Room_ID`),
  UNIQUE KEY `unique_room_per_hostel` (`Hostel_ID`,`Room_Number`),
  CONSTRAINT `fk_room_hostel` FOREIGN KEY (`Hostel_ID`) REFERENCES `Hostels` (`Hostel_ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `Rooms_chk_1` CHECK ((`Capacity` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Rooms`
--

LOCK TABLES `Rooms` WRITE;
/*!40000 ALTER TABLE `Rooms` DISABLE KEYS */;
INSERT INTO `Rooms` VALUES (201,'101',1,1,2),(202,'102',1,1,2),(203,'201',3,2,2),(204,'202',3,2,2),(205,'301',5,3,2),(206,'302',5,3,2),(207,'101',7,1,3),(208,'102',7,1,3),(209,'201',9,2,2),(210,'202',9,2,2);
/*!40000 ALTER TABLE `Rooms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Visitor_Logs`
--

DROP TABLE IF EXISTS `Visitor_Logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Visitor_Logs` (
  `Log_ID` int NOT NULL,
  `Visitor_Name` varchar(150) NOT NULL,
  `Contact_Number` varchar(15) NOT NULL,
  `ID_Proof_Type` varchar(50) NOT NULL,
  `ID_Proof_Number` varchar(100) NOT NULL,
  `Host_Member_ID` int NOT NULL,
  `Entry_Time` timestamp NOT NULL,
  `Purpose` varchar(255) NOT NULL,
  PRIMARY KEY (`Log_ID`),
  UNIQUE KEY `ID_Proof_Number` (`ID_Proof_Number`),
  KEY `fk_visitor_host` (`Host_Member_ID`),
  CONSTRAINT `fk_visitor_host` FOREIGN KEY (`Host_Member_ID`) REFERENCES `Members` (`Member_ID`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Visitor_Logs`
--

LOCK TABLES `Visitor_Logs` WRITE;
/*!40000 ALTER TABLE `Visitor_Logs` DISABLE KEYS */;
INSERT INTO `Visitor_Logs` VALUES (501,'Rajesh Karmali','9123456701','Aadhar','ID202501',101,'2025-02-10 04:45:00','Parent visit'),(502,'Suresh Kumar','9123456702','PAN','ID202502',102,'2025-02-11 09:00:00','Family visit'),(503,'Mahesh Patil','9123456703','Aadhar','ID202503',103,'2025-02-12 11:15:00','Relative visit'),(504,'Anil Kale','9123456704','Driving License','ID202504',104,'2025-02-13 05:50:00','Parent visit'),(505,'Ravi Kumar','9123456705','Aadhar','ID202505',105,'2025-02-14 11:40:00','Friend visit'),(506,'Courier Agent','9123456706','Company ID','ID202506',101,'2025-02-15 07:35:00','Package delivery'),(507,'Food Delivery','9123456707','Company ID','ID202507',102,'2025-02-16 13:55:00','Food delivery'),(508,'Guardian','9123456708','Aadhar','ID202508',103,'2025-02-17 04:10:00','Guardian visit'),(509,'Friend','9123456709','Aadhar','ID202509',104,'2025-02-18 12:30:00','Friend visit'),(510,'Parent','9123456710','PAN','ID202510',105,'2025-02-19 07:20:00','Parent visit');
/*!40000 ALTER TABLE `Visitor_Logs` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-14  1:01:56
