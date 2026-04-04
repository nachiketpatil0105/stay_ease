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


-- 2. Insert the Golden Dataset Credentials
-- We are mapping these directly to the Member_IDs
INSERT INTO `user_credentials` (`Member_ID`, `Username`, `Password_Hash`) VALUES 
-- The Overall Admin
(100, 'admin', 'scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9'),

-- The Wardens
(102, 'riya', 'scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9'),
(106, 'rakesh', 'scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9'),
(108, 'vikram', 'scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9'),

-- The Students
(110, 'priya', 'scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9'),
(111, 'ananya', 'scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9'),
(112, 'rahul', 'scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9'),
(113, 'karan', 'scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9'),
(114, 'amit', 'scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9'),
(115, 'rohan', 'scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9'),
(116, 'neha', 'scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9'),
(117, 'sneha', 'scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9'),
(118, 'arjun', 'scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9'),
(119, 'kabir', 'scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9'),

-- The Security
(120,'security', 'scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9'),
(122,'secrity_h1', 'scrypt:32768:8:1$9TavVd47KiaIiyzx$7461c666f54e44b08b4d2a7494aa2c799eecb2a9dede602c805b697ec1bb1bbbae10d9a61b3c42b2d2b087dd14d133249e8a0e5ca07f360466591fdcd8f632a9');