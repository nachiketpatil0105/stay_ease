# 🏨 StayEase – Hostel Management System (MySQL Schema)

> **Note:** Attribute options are explicitly defined where required.  
> Foreign Keys, `CHECK`, `UNIQUE`, and logical constraints are included where MySQL allows them.

---

## 🟢 Database Creation
```sql
CREATE DATABASE stayease;
USE stayease;
```

---

## 1️⃣ Roles

```sql
CREATE TABLE Roles (
    Role_ID INT AUTO_INCREMENT PRIMARY KEY,
    Role_Name VARCHAR(50) NOT NULL UNIQUE,
    Description TEXT NOT NULL
);
```

---

## 2️⃣ Members

```sql
CREATE TABLE Members (
    Member_ID INT AUTO_INCREMENT PRIMARY KEY,
    First_Name VARCHAR(100) NOT NULL,
    Last_Name VARCHAR(100),
    Gender VARCHAR(20) NOT NULL,
    Age INT NOT NULL CHECK (Age > 0),
    Contact_Number VARCHAR(15) NOT NULL UNIQUE,
    Email VARCHAR(100) NOT NULL UNIQUE,
    Emergency_Contact VARCHAR(15) NOT NULL,
    Image_Path VARCHAR(255),
    Role_ID INT NOT NULL,
    Status VARCHAR(20) NOT NULL CHECK (Status IN ('Active', 'Inactive')),
    
    CONSTRAINT fk_members_role
        FOREIGN KEY (Role_ID)
        REFERENCES Roles(Role_ID)
        ON DELETE RESTRICT
);
```

---

## 3️⃣ Hostels

```sql
CREATE TABLE Hostels (
    Hostel_ID INT AUTO_INCREMENT PRIMARY KEY,
    Hostel_Name VARCHAR(100) NOT NULL UNIQUE,
    Hostel_Type VARCHAR(20) NOT NULL,
    Total_Floors INT NOT NULL,
    Warden_ID INT NOT NULL,

    CONSTRAINT fk_hostel_warden
        FOREIGN KEY (Warden_ID)
        REFERENCES Members(Member_ID)
        ON DELETE RESTRICT
);
```

---

## 4️⃣ Rooms

```sql
CREATE TABLE Rooms (
    Room_ID INT AUTO_INCREMENT PRIMARY KEY,
    Room_Number VARCHAR(20) NOT NULL,
    Hostel_ID INT NOT NULL,
    Floor_Number INT NOT NULL,
    Capacity INT NOT NULL CHECK (Capacity > 0),

    CONSTRAINT uq_room_per_hostel UNIQUE (Hostel_ID, Room_Number),

    CONSTRAINT fk_rooms_hostel
        FOREIGN KEY (Hostel_ID)
        REFERENCES Hostels(Hostel_ID)
        ON DELETE CASCADE
);
```

📌 **Room occupancy** is derived using **active room allocations**.

---

## 5️⃣ Room_Allocations

```sql
CREATE TABLE Room_Allocations (
    Allocation_ID INT AUTO_INCREMENT PRIMARY KEY,
    Member_ID INT NOT NULL,
    Room_ID INT NOT NULL,
    Allocation_Date DATE NOT NULL,
    Check_Out_Date DATE,
    Status VARCHAR(20) NOT NULL CHECK (Status IN ('Active', 'Inactive')),

    CONSTRAINT chk_allocation_dates
        CHECK (Check_Out_Date > Allocation_Date OR Check_Out_Date IS NULL),

    CONSTRAINT fk_allocation_member
        FOREIGN KEY (Member_ID)
        REFERENCES Members(Member_ID)
        ON DELETE RESTRICT,

    CONSTRAINT fk_allocation_room
        FOREIGN KEY (Room_ID)
        REFERENCES Rooms(Room_ID)
        ON DELETE RESTRICT
);
```

📌 **Application-level rule:**
➡️ One member can have **only one Active allocation** at a time.

---

## 6️⃣ Furniture_Inventory

```sql
CREATE TABLE Furniture_Inventory (
    Furniture_ID INT AUTO_INCREMENT PRIMARY KEY,
    Item_Name VARCHAR(100) NOT NULL,
    Room_ID INT NOT NULL,
    Purchase_Date DATE NOT NULL,
    Current_Condition VARCHAR(50) NOT NULL,

    CONSTRAINT fk_furniture_room
        FOREIGN KEY (Room_ID)
        REFERENCES Rooms(Room_ID)
        ON DELETE CASCADE
);
```

---

## 7️⃣ Visitors

```sql
CREATE TABLE Visitors (
    Visitor_ID INT AUTO_INCREMENT PRIMARY KEY,
    Visitor_Name VARCHAR(100) NOT NULL,
    Contact_Number VARCHAR(15) NOT NULL UNIQUE,
    ID_Proof_Type VARCHAR(50) NOT NULL,
    ID_Proof_Number VARCHAR(50) NOT NULL UNIQUE
);
```

---

## 8️⃣ Visitor_Logs

```sql
CREATE TABLE Visitor_Logs (
    Log_ID INT AUTO_INCREMENT PRIMARY KEY,
    Visitor_ID INT NOT NULL,
    Host_Member_ID INT NOT NULL,
    Entry_Time TIMESTAMP NOT NULL,
    Exit_Time TIMESTAMP,
    Purpose VARCHAR(255) NOT NULL,

    CONSTRAINT chk_visitor_time
        CHECK (Exit_Time > Entry_Time OR Exit_Time IS NULL),

    CONSTRAINT fk_log_visitor
        FOREIGN KEY (Visitor_ID)
        REFERENCES Visitors(Visitor_ID)
        ON DELETE RESTRICT,

    CONSTRAINT fk_log_host
        FOREIGN KEY (Host_Member_ID)
        REFERENCES Members(Member_ID)
        ON DELETE RESTRICT
);
```

---

## 9️⃣ Member_Movement_Logs

```sql
CREATE TABLE Member_Movement_Logs (
    Movement_ID INT AUTO_INCREMENT PRIMARY KEY,
    Member_ID INT NOT NULL,
    Exit_Time TIMESTAMP NOT NULL,
    Entry_Time TIMESTAMP,
    Purpose VARCHAR(255) NOT NULL,

    CONSTRAINT chk_member_movement_time
        CHECK (Entry_Time > Exit_Time OR Entry_Time IS NULL),

    CONSTRAINT fk_movement_member
        FOREIGN KEY (Member_ID)
        REFERENCES Members(Member_ID)
        ON DELETE RESTRICT
);
```

---

## 🔟 Fee_Structures

```sql
CREATE TABLE Fee_Structures (
    Fee_Type_ID INT AUTO_INCREMENT PRIMARY KEY,
    Fee_Name VARCHAR(100) NOT NULL,
    Amount DECIMAL(10,2) NOT NULL,
    Academic_Year VARCHAR(20) NOT NULL
);
```

---

## 1️⃣1️⃣ Payments

```sql
CREATE TABLE Payments (
    Payment_ID INT AUTO_INCREMENT PRIMARY KEY,
    Member_ID INT NOT NULL,
    Fee_Type_ID INT NOT NULL,
    Payment_Date DATE NOT NULL,
    Amount_Paid DECIMAL(10,2) NOT NULL,
    Payment_Status VARCHAR(20) NOT NULL CHECK (Payment_Status IN ('Success', 'Failed')),
    Transaction_Reference VARCHAR(100) NOT NULL UNIQUE,

    CONSTRAINT fk_payment_member
        FOREIGN KEY (Member_ID)
        REFERENCES Members(Member_ID)
        ON DELETE RESTRICT,

    CONSTRAINT fk_payment_fee
        FOREIGN KEY (Fee_Type_ID)
        REFERENCES Fee_Structures(Fee_Type_ID)
        ON DELETE RESTRICT
);
```

---

## 1️⃣2️⃣ Complaint_Types

```sql
CREATE TABLE Complaint_Types (
    Complaint_Type_ID INT AUTO_INCREMENT PRIMARY KEY,
    Type_Name VARCHAR(100) NOT NULL,
    Sub_Type VARCHAR(100) NOT NULL
);
```

---

## 1️⃣3️⃣ Complaints

```sql
CREATE TABLE Complaints (
    Complaint_ID INT AUTO_INCREMENT PRIMARY KEY,
    Member_ID INT NOT NULL,
    Complaint_Type_ID INT NOT NULL,
    Description TEXT NOT NULL,
    Submission_Date DATE NOT NULL,
    Resolved_Date DATE,
    Status VARCHAR(20) NOT NULL
        CHECK (Status IN ('Pending', 'In Progress', 'Resolved')),

    CONSTRAINT fk_complaint_member
        FOREIGN KEY (Member_ID)
        REFERENCES Members(Member_ID)
        ON DELETE RESTRICT,

    CONSTRAINT fk_complaint_type
        FOREIGN KEY (Complaint_Type_ID)
        REFERENCES Complaint_Types(Complaint_Type_ID)
        ON DELETE RESTRICT
);
```

📌 **Logical Rule (Documented):**
If `Status = 'Resolved'` → `Resolved_Date IS NOT NULL`

---

## 1️⃣4️⃣ Complaint_Logs

```sql
CREATE TABLE Complaint_Logs (
    Log_ID INT AUTO_INCREMENT PRIMARY KEY,
    Complaint_ID INT NOT NULL,
    Action_By INT NOT NULL,
    Action_Date TIMESTAMP NOT NULL,
    Remarks TEXT NOT NULL,

    CONSTRAINT fk_log_complaint
        FOREIGN KEY (Complaint_ID)
        REFERENCES Complaints(Complaint_ID)
        ON DELETE CASCADE,

    CONSTRAINT fk_log_action_by
        FOREIGN KEY (Action_By)
        REFERENCES Members(Member_ID)
        ON DELETE RESTRICT
);
```

