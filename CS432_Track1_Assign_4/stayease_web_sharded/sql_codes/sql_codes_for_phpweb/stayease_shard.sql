-- Even though the SQL code from the dump was perfectly valid, the specific version of  
-- phpMyAdmin or MySQL running on the IITGN cluster has a buggy SQL parser. When it 
-- reads the word CHECK in the constraints, it gets confused and mistakenly thinks  
-- we are trying to name a column "CHECK", which triggers that exact error.


-- Member
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
  KEY `fk_member_role` (`Role_ID`)
);

-- Rooms
CREATE TABLE `rooms` (
  `Room_ID` int NOT NULL,
  `Room_Number` varchar(20) NOT NULL,
  `Hostel_ID` int NOT NULL,
  `Floor_Number` int NOT NULL,
  `Capacity` int NOT NULL,
  PRIMARY KEY (`Room_ID`),
  UNIQUE KEY `unique_room_per_hostel` (`Hostel_ID`,`Room_Number`)
);


-- Room Allocations
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
  KEY `idx_room_allocations_member_status` (`Member_ID`,`Status`)
);

-- ROLES
CREATE TABLE `roles` (
  `Role_ID` int NOT NULL,
  `Role_Name` varchar(100) NOT NULL,
  `Description` text NOT NULL,
  PRIMARY KEY (`Role_ID`),
  UNIQUE KEY `Role_Name` (`Role_Name`)
);


-- HOSTELS
CREATE TABLE `hostels` (
  `Hostel_ID` int NOT NULL,
  `Hostel_Name` varchar(150) NOT NULL,
  `Hostel_Type` varchar(5) NOT NULL,
  `Total_Floors` int NOT NULL,
  `Warden_ID` int NOT NULL,
  `Security_ID` int DEFAULT NULL,
  PRIMARY KEY (`Hostel_ID`),
  UNIQUE KEY `Hostel_Name` (`Hostel_Name`)
);


-- COMPLAINT_TYPES
CREATE TABLE `complaint_types` (
  `Complaint_Type_ID` int NOT NULL,
  `Type_Name` varchar(100) NOT NULL,
  `Sub_Type` varchar(100) NOT NULL,
  PRIMARY KEY (`Complaint_Type_ID`)
);


-- Complaints
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
  KEY `fk_complaint_type` (`Complaint_Type_ID`)
);