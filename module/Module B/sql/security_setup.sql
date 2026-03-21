USE stayease;

-- 1. Create the Core System Data table for authentication
CREATE TABLE `user_credentials` (
  `Member_ID` INT NOT NULL,
  `Username` VARCHAR(100) NOT NULL UNIQUE,
  `Password_Hash` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`Member_ID`),
  CONSTRAINT `fk_credentials_member` 
    FOREIGN KEY (`Member_ID`) 
    REFERENCES `members` (`Member_ID`) 
    ON DELETE CASCADE 
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 2. Insert Mock Data for Testing
-- Note: In a real app, passwords are never plain text. 
-- These strings simulate what a hashed password looks like for testing the Python API.
INSERT INTO `user_credentials` (`Member_ID`, `Username`, `Password_Hash`) 
VALUES 
(1, 'admin', 'scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9'),
(2, 'student1', 'scrypt:32768:8:1$student_mock_hash');