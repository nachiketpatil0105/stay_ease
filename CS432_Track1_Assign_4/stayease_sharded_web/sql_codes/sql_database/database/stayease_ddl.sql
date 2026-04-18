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
-- Table structure for table `complaint_types`
--

DROP TABLE IF EXISTS `complaint_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `complaint_types` (
  `Complaint_Type_ID` int NOT NULL,
  `Type_Name` varchar(100) NOT NULL,
  `Sub_Type` varchar(100) NOT NULL,
  PRIMARY KEY (`Complaint_Type_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `complaints`
--

DROP TABLE IF EXISTS `complaints`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `complaints` (
  `Complaint_ID` int NOT NULL AUTO_INCREMENT,
  `Member_ID` int NOT NULL,
  `Complaint_Type_ID` int NOT NULL,
  `Description` text NOT NULL,
  `Submission_Date` date NOT NULL,
  `Resolved_Date` date DEFAULT NULL,
  `Status` varchar(20) NOT NULL,
  PRIMARY KEY (`Complaint_ID`),
  KEY `fk_complaint_member` (`Member_ID`),
  KEY `fk_complaint_type` (`Complaint_Type_ID`),
  KEY `idx_complaints_member_date` (`Member_ID`,`Submission_Date`),
  CONSTRAINT `fk_complaint_member` FOREIGN KEY (`Member_ID`) REFERENCES `members` (`Member_ID`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_complaint_type` FOREIGN KEY (`Complaint_Type_ID`) REFERENCES `complaint_types` (`Complaint_Type_ID`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `chk_resolution_logic` CHECK ((((`Status` = _utf8mb4'Resolved') and (`Resolved_Date` is not null)) or (`Status` in (_utf8mb4'Pending',_utf8mb4'In Progress')))),
  CONSTRAINT `complaints_chk_1` CHECK ((`Status` in (_utf8mb4'Pending',_utf8mb4'In Progress',_utf8mb4'Resolved')))
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `fee_structures`
--

DROP TABLE IF EXISTS `fee_structures`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fee_structures` (
  `Fee_Type_ID` int NOT NULL,
  `Fee_Name` varchar(150) NOT NULL,
  `Amount` decimal(10,2) NOT NULL,
  `Academic_Year` varchar(20) NOT NULL,
  PRIMARY KEY (`Fee_Type_ID`),
  CONSTRAINT `fee_structures_chk_1` CHECK ((`Amount` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `furniture_inventory`
--

DROP TABLE IF EXISTS `furniture_inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `furniture_inventory` (
  `Furniture_ID` int NOT NULL AUTO_INCREMENT,
  `Item_Name` varchar(100) NOT NULL,
  `Room_ID` int NOT NULL,
  `Purchase_Date` date NOT NULL,
  `Current_Condition` varchar(7) NOT NULL,
  PRIMARY KEY (`Furniture_ID`),
  KEY `fk_furniture_room` (`Room_ID`),
  CONSTRAINT `fk_furniture_room` FOREIGN KEY (`Room_ID`) REFERENCES `rooms` (`Room_ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `furniture_inventory_chk_1` CHECK ((`Current_Condition` in (_utf8mb4'Good',_utf8mb4'Damaged')))
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hostels`
--

DROP TABLE IF EXISTS `hostels`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hostels` (
  `Hostel_ID` int NOT NULL,
  `Hostel_Name` varchar(150) NOT NULL,
  `Hostel_Type` varchar(5) NOT NULL,
  `Total_Floors` int NOT NULL,
  `Warden_ID` int NOT NULL,
  `Security_ID` int DEFAULT NULL,
  PRIMARY KEY (`Hostel_ID`),
  UNIQUE KEY `Hostel_Name` (`Hostel_Name`),
  KEY `fk_hostel_warden` (`Warden_ID`),
  KEY `fk_hostel_security` (`Security_ID`),
  CONSTRAINT `fk_hostel_security` FOREIGN KEY (`Security_ID`) REFERENCES `members` (`Member_ID`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_hostel_warden` FOREIGN KEY (`Warden_ID`) REFERENCES `members` (`Member_ID`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `hostels_chk_1` CHECK ((`Hostel_Type` in (_utf8mb4'Boys',_utf8mb4'Girls'))),
  CONSTRAINT `hostels_chk_2` CHECK ((`Total_Floors` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `member_movement_logs`
--

DROP TABLE IF EXISTS `member_movement_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `member_movement_logs` (
  `Movement_ID` int NOT NULL AUTO_INCREMENT,
  `Member_ID` int NOT NULL,
  `Exit_Time` timestamp NOT NULL,
  `Entry_Time` timestamp NULL DEFAULT NULL,
  `Purpose` varchar(255) NOT NULL,
  PRIMARY KEY (`Movement_ID`),
  KEY `fk_movement_member` (`Member_ID`),
  CONSTRAINT `fk_movement_member` FOREIGN KEY (`Member_ID`) REFERENCES `members` (`Member_ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `chk_movement_time` CHECK (((`Entry_Time` > `Exit_Time`) or (`Entry_Time` is null)))
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `members`
--

DROP TABLE IF EXISTS `members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `members` (
  `Member_ID` int NOT NULL AUTO_INCREMENT,
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
  CONSTRAINT `fk_member_role` FOREIGN KEY (`Role_ID`) REFERENCES `roles` (`Role_ID`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `members_chk_1` CHECK ((`Gender` in (_utf8mb4'M',_utf8mb4'F'))),
  CONSTRAINT `members_chk_2` CHECK ((`Age` > 0)),
  CONSTRAINT `members_chk_3` CHECK ((`Status` in (_utf8mb4'Active',_utf8mb4'Inactive')))
) ENGINE=InnoDB AUTO_INCREMENT=126 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payments` (
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
  KEY `idx_payments_member_date` (`Member_ID`,`Payment_Date`),
  CONSTRAINT `fk_payment_fee` FOREIGN KEY (`Fee_Type_ID`) REFERENCES `fee_structures` (`Fee_Type_ID`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_payment_member` FOREIGN KEY (`Member_ID`) REFERENCES `members` (`Member_ID`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `payments_chk_1` CHECK ((`Amount_Paid` > 0)),
  CONSTRAINT `payments_chk_2` CHECK ((`Payment_Status` in (_utf8mb4'Success',_utf8mb4'Failed')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `Role_ID` int NOT NULL,
  `Role_Name` varchar(100) NOT NULL,
  `Description` text NOT NULL,
  PRIMARY KEY (`Role_ID`),
  UNIQUE KEY `Role_Name` (`Role_Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `room_allocations`
--

DROP TABLE IF EXISTS `room_allocations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `room_allocations` (
  `Allocation_ID` int NOT NULL AUTO_INCREMENT,
  `Member_ID` int NOT NULL,
  `Room_ID` int NOT NULL,
  `Allocation_Date` date NOT NULL,
  `Check_Out_Date` date DEFAULT NULL,
  `Status` varchar(20) NOT NULL,
  PRIMARY KEY (`Allocation_ID`),
  KEY `fk_allocation_member` (`Member_ID`),
  KEY `fk_allocation_room` (`Room_ID`),
  KEY `idx_room_allocations_member_status` (`Member_ID`,`Status`),
  CONSTRAINT `fk_allocation_member` FOREIGN KEY (`Member_ID`) REFERENCES `members` (`Member_ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_allocation_room` FOREIGN KEY (`Room_ID`) REFERENCES `rooms` (`Room_ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `chk_checkout_date` CHECK (((`Check_Out_Date` > `Allocation_Date`) or (`Check_Out_Date` is null))),
  CONSTRAINT `room_allocations_chk_1` CHECK ((`Status` in (_utf8mb4'Active',_utf8mb4'Inactive')))
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `rooms`
--

DROP TABLE IF EXISTS `rooms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rooms` (
  `Room_ID` int NOT NULL,
  `Room_Number` varchar(20) NOT NULL,
  `Hostel_ID` int NOT NULL,
  `Floor_Number` int NOT NULL,
  `Capacity` int NOT NULL,
  PRIMARY KEY (`Room_ID`),
  UNIQUE KEY `unique_room_per_hostel` (`Hostel_ID`,`Room_Number`),
  CONSTRAINT `fk_room_hostel` FOREIGN KEY (`Hostel_ID`) REFERENCES `hostels` (`Hostel_ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `rooms_chk_1` CHECK ((`Capacity` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_credentials`
--

DROP TABLE IF EXISTS `user_credentials`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_credentials` (
  `Member_ID` int NOT NULL,
  `Username` varchar(100) NOT NULL,
  `Password_Hash` varchar(255) NOT NULL,
  PRIMARY KEY (`Member_ID`),
  UNIQUE KEY `Username` (`Username`),
  CONSTRAINT `fk_credentials_member` FOREIGN KEY (`Member_ID`) REFERENCES `members` (`Member_ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitor_logs`
--

DROP TABLE IF EXISTS `visitor_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `visitor_logs` (
  `Log_ID` int NOT NULL AUTO_INCREMENT,
  `Visitor_Name` varchar(150) NOT NULL,
  `Contact_Number` varchar(15) NOT NULL,
  `ID_Proof_Type` varchar(50) NOT NULL,
  `ID_Proof_Number` varchar(100) NOT NULL,
  `Host_Member_ID` int NOT NULL,
  `Entry_Time` timestamp NOT NULL,
  `Exit_Time` timestamp NULL DEFAULT NULL,
  `Purpose` varchar(255) NOT NULL,
  PRIMARY KEY (`Log_ID`),
  KEY `fk_visitor_host` (`Host_Member_ID`),
  CONSTRAINT `fk_visitor_host` FOREIGN KEY (`Host_Member_ID`) REFERENCES `members` (`Member_ID`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-21 18:39:52
