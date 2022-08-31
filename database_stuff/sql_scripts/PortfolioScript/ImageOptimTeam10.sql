-- Database Creation Script 
-- Schema creation
CREATE SCHEMA IF NOT EXISTS imageoptimteam10;
USE imageoptimteam10;
-- Table creations
CREATE TABLE IF NOT EXISTS `CompanyTypes` (
  `SizeID` INT NOT NULL,
  `SizeType` VARCHAR(45) NOT NULL,
  `SizePriceAddon` DOUBLE NOT NULL,
  PRIMARY KEY (`SizeID`)
);
CREATE TABLE IF NOT EXISTS `Countries` (
  `CountryID` INT NOT NULL,
  `CountryName` VARCHAR(45) NOT NULL,
  `VATApplicable` BOOLEAN NOT NULL,
  PRIMARY KEY (`CountryID`)
);
CREATE TABLE IF NOT EXISTS `Users` (
  `UserID` INT NOT NULL AUTO_INCREMENT,
  `UserEmail` VARCHAR(45) NOT NULL,
  `UserPassword` VARCHAR(45) NOT NULL,
  `CompanyName` VARCHAR(45) NOT NULL,
  `ContactName` VARCHAR(45) NOT NULL,
  `CompanyAddress` VARCHAR(90) NULL,
  `Admin` BOOLEAN DEFAULT false,
  `Countries_CountryID` INT,
  `CompanyTypes_SizeID` INT,
  PRIMARY KEY (
    `UserID`,
    `CompanyTypes_SizeID`,
    `Countries_CountryID`
  ),
  CONSTRAINT `fk_Users_CompanyTypes1` FOREIGN KEY (`CompanyTypes_SizeID`) REFERENCES companytypes (`SizeID`) ON DELETE CASCADE ON UPDATE cascade,
  CONSTRAINT `fk_Users_CountryID1` FOREIGN KEY (`Countries_CountryID`) REFERENCES countries (`CountryID`) ON DELETE CASCADE ON UPDATE cascade
);
CREATE TABLE IF NOT EXISTS `Products` (
  `ProductID` INT NOT NULL,
  `ProductPrice` DOUBLE NOT NULL,
  `ProductName` VARCHAR(45) NOT NULL,
  `ProductDescription` VARCHAR(300) NOT NULL,
  `ProductImage` VARCHAR(150) NOT NULL,
  PRIMARY KEY (`ProductID`)
);
CREATE TABLE IF NOT EXISTS `Licenses` (
  `LicenseID` INT NOT NULL,
  `LicenseType` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`LicenseID`)
);
CREATE TABLE IF NOT EXISTS `PromoCodes` (
  `PromoID` INT NOT NULL AUTO_INCREMENT,
  `PromoCode` VARCHAR(45) NOT NULL,
  `DiscountPercent` DOUBLE,
  `SetDiscount` DOUBLE,
  `ValidUser` INT NOT NULL,
  PRIMARY KEY (`PromoID`)
);
CREATE TABLE IF NOT EXISTS `PurchaseLog` (
  `PurchaseID` INT NOT NULL AUTO_INCREMENT,
  `PurchasePrice` DOUBLE NOT NULL,
  `PurchaseDate` VARCHAR(45) NOT NULL,
  `Products_ProductID` INT NOT NULL,
  `Licenses_LicenseID` INT NOT NULL,
  `CompanyTypes_SizeID` INT NOT NULL,
  `Users_UserID` INT NOT NULL,
  `PromoCodes_PromoID` INT DEFAULT NULL,
  PRIMARY KEY (
    `PurchaseID`,
    `Products_ProductID`,
    `Licenses_LicenseID`,
    `CompanyTypes_SizeID`,
    `Users_UserID`
  ),
  CONSTRAINT `fk_Purchase Log_Products1` FOREIGN KEY (`Products_ProductID`) REFERENCES `Products` (`ProductID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_Purchase Log_Licenses1` FOREIGN KEY (`Licenses_LicenseID`) REFERENCES `Licenses` (`LicenseID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_Purchase Log_CompanyTypes1` FOREIGN KEY (`CompanyTypes_SizeID`) REFERENCES `CompanyTypes` (`SizeID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_Purchase Log_UserID1` FOREIGN KEY (`Users_UserID`) REFERENCES `Users` (`UserID`) ON DELETE CASCADE ON UPDATE CASCADE
);
-- "ContactLog" 
CREATE TABLE IF NOT EXISTS `ContactLog` (
  `ContactID` INT NOT NULL AUTO_INCREMENT,
  `FirstName` VARCHAR(80),
  `LastName` VARCHAR(100),
  `Email` VARCHAR(100),
  `Number` VARCHAR(60),
  `Message` VARCHAR(255),
  PRIMARY KEY (`ContactID`)
);
CREATE TABLE IF NOT EXISTS `Audits` (
  `AuditID` INT NOT NULL AUTO_INCREMENT,
  `TableAltered` VARCHAR(45) NOT NULL,
  `RecordPrimKey` INT NOT NULL,
  `FieldAltered` VARCHAR(45) NOT NULL,
  `OldData` VARCHAR(200),
  `NewData` VARCHAR(200),
  PRIMARY KEY (`AuditID`)
);


-- Stored Procedures 
-- "completepurchase" - runs when a puchase is completed
DELIMITER //
CREATE DEFINER=`root`@`localhost` PROCEDURE `CompletePurchase`(IN p_PurchasePrice double,IN p_PurchaseDate varchar(45), IN p_Products_ProductID int, IN p_Licenses_LicenseID int, IN p_CompanyTypes_SizeID int, IN p_Users_UserID int, IN p_PromoCodes_PromoID int)
BEGIN
	INSERT INTO purchaselog (PurchasePrice, PurchaseDate, Products_ProductID, Licenses_LicenseID, CompanyTypes_SizeID, Users_UserID,PromoCodes_PromoID) VALUES (p_PurchasePrice, p_PurchaseDate, p_Products_ProductID, p_Licenses_LicenseID, p_CompanyTypes_SizeID, p_Users_UserID, p_PromoCodes_PromoID);
END;

-- "createuser" - runs when a new user is created
DELIMITER //
CREATE DEFINER=`root`@`localhost` PROCEDURE `CreateUser`(IN p_UserEmail VARCHAR(45), IN p_UserPassword VARCHAR(45), IN p_CompanyName VARCHAR(45), IN p_ContactName VARCHAR(45), IN p_CompanyAddress VARCHAR(45), IN p_Countries_CountryID INT, IN p_CompanyTypes_SizeID INT)
BEGIN
	INSERT INTO users (UserEmail, UserPassword, CompanyName, ContactName, CompanyAddress,Countries_CountryID, CompanyTypes_SizeID) VALUES (p_UserEmail, p_UserPassword, p_CompanyName, p_ContactName, p_CompanyAddress,p_Countries_CountryID, p_CompanyTypes_SizeID);
END;


-- Sample Insertion Data 
-- "CompanyTypes" Table:
INSERT INTO companytypes (SizeID, SizeType,SizePriceAddon) VALUES (0, "Individual", 950.00);
INSERT INTO companytypes (SizeID, SizeType,SizePriceAddon) VALUES (1, "1 - 9", 950.00);
INSERT INTO companytypes (SizeID, SizeType,SizePriceAddon) VALUES (2, "10 - 49", 1250.00);
INSERT INTO companytypes (SizeID, SizeType,SizePriceAddon) VALUES (3, "50 - 99", 1650.00);
INSERT INTO companytypes (SizeID, SizeType,SizePriceAddon) VALUES (4, "100 - 249", 2450.00);
INSERT INTO companytypes (SizeID, SizeType,SizePriceAddon) VALUES (5, "250 - 499", 3950.00);
INSERT INTO companytypes (SizeID, SizeType,SizePriceAddon) VALUES (6, "500 - 999", 9950.00);
INSERT INTO companytypes (SizeID, SizeType,SizePriceAddon) VALUES (7, "1000 - 2999", 15950.00);
INSERT INTO companytypes (SizeID, SizeType,SizePriceAddon) VALUES (8, "3000 or more", 25500.00);

-- "Countries" Table:
INSERT INTO countries (CountryID, CountryName, VATApplicable) VALUES (1, "Europe", true);
INSERT INTO countries (CountryID, CountryName, VATApplicable) VALUES (2, "USA", false);

-- "Licenses" Table:
INSERT INTO licenses (LicenseID, LicenseType) VALUES (0, "Annual");
INSERT INTO licenses (LicenseID, LicenseType) VALUES (1, "Perpetual");

-- "Products" Table
INSERT INTO products(ProductID, ProductPrice, ProductName, ProductDescription, ProductImage) VALUES (1, 99, 'Photoshop', 'Adobe Photoshop is the predominant photo editing and manipulation software on the market. Its uses range from the full-featured editing of large batches of photos to creating intricate digital paintings and drawings that mimic those done by hand.', 'https://mk0camerajabberhe53n.kinstacdn.com/wp-content/uploads/2017/12/photoshop_cc_2018_review-04.jpg');
INSERT INTO products(ProductID, ProductPrice, ProductName, ProductDescription, ProductImage) VALUES (2, 20, 'BitDefender', 'Bitdefender develops and markets cybersecurity products and services for companies and consumers including endpoint protection (with hardening and risk analytics capabilities), extended detection and response, multi-cloud security, and managed detection and response, antivirus software, IoT security', 'https://www.security.org/wp-content/uploads/2020/12/Bitdefender-Dashboard.png');
INSERT INTO products(ProductID, ProductPrice, ProductName, ProductDescription, ProductImage) VALUES (3, 20, 'Steam', 'Steam is a video game digital distribution service by Valve. It was launched as a standalone software client in September 2003 as a way for Valve to provide automatic updates for their games, and expanded to include games from third-party publishers.', 'https://cdn.akamai.steamstatic.com/store/about/social-og.jpg');

-- "PromoCodes" Table
INSERT INTO PromoCodes (PromoCode, DiscountPercent, ValidUser) VALUES ("XERF2R", 50.0, 0);
INSERT INTO PromoCodes (PromoCode, SetDiscount, ValidUser) VALUES ("5RX1PZ", 50.0, 1);

-- "Users" Table (passwords entered are encrypted values representing the decrypted value of "password")
INSERT INTO Users (UserEmail, UserPassword,CompanyName,ContactName,CompanyAddress,Admin, Countries_CountryID, CompanyTypes_SizeID) VALUES ("example@admin.com", "BTZG)aC,","company","example","exampleaddress",false, 1, 1);
INSERT INTO Users (UserEmail, UserPassword,CompanyName,ContactName,CompanyAddress,Admin, Countries_CountryID, CompanyTypes_SizeID) VALUES ("admin@admin.com", "BTZG)aC,","company","admin","adminaddress",true, 1, 1);
INSERT INTO Users (UserEmail, UserPassword,CompanyName,ContactName,CompanyAddress,Admin, Countries_CountryID, CompanyTypes_SizeID) VALUES ("gillj8@cardiff.ac.uk", "BTZG)aC,", "cardiff uni", "Josh", "University of Cardiff", false, 1, 3);

-- "PurchaseLog" Table
INSERT INTO PurchaseLog (PurchasePrice, PurchaseDate, Products_ProductID, Licenses_LicenseID, CompanyTypes_SizeID, Users_UserID) VALUES (1250.0, "03/03/2021", 3, 1, 3, 3);
INSERT INTO PurchaseLog (PurchasePrice, PurchaseDate, Products_ProductID, Licenses_LicenseID, CompanyTypes_SizeID, Users_UserID, PromoCodes_PromoID) VALUES (2570.0, "27/04/2021", 2, 1, 1, 2, 0);
INSERT INTO PurchaseLog (PurchasePrice, PurchaseDate, Products_ProductID, Licenses_LicenseID, CompanyTypes_SizeID, Users_UserID) VALUES (9750.0, "19/04/2021", 1, 0, 3, 1);
INSERT INTO PurchaseLog (PurchasePrice, PurchaseDate, Products_ProductID, Licenses_LicenseID, CompanyTypes_SizeID, Users_UserID) VALUES (12050.0, "01/05/2021", 2, 0, 3, 3);


-- Test Queries 
-- Basic selects for each table
SELECT * FROM CompanyTypes;
SELECT * FROM Countries;
SELECT * FROM Licenses;
SELECT * FROM Products;
SELECT * FROM PromoCodes;
SELECT * FROM PurchaseLog;
SELECT * FROM Users;

-- More advanced selects
-- Select user email and password for a specific ID
SELECT UserEmail, UserPassword FROM Users WHERE UserID = 1;

-- Select purchase log for a specifc user based on user email
SELECT * FROM PurchaseLog WHERE Users_UserID = (
  SELECT UserID FROM Users WHERE UserEmail = "example@admin.com"
);
SELECT * FROM PurchaseLog WHERE Users_UserID = (
  SELECT UserID FROM Users WHERE UserEmail = "gillj8@cardiff.ac.uk"
);

-- Select purchase log for a specific product based on product name
SELECT * FROM PurchaseLog WHERE Products_ProductID = (
  SELECT ProductID FROM Products WHERE ProductName = "Steam"
);

-- Select user data based on a purchase id on a specifc date
SELECT * FROM Users WHERE UserID = (
  SELECT Users_UserID FROM PurchaseLog WHERE PurchaseDate = "19/04/2021"
);

-- Select product data based on id from a purchase made by a specifc user on a specific date
SELECT * FROM Products WHERE ProductID = (
  SELECT Products_ProductID FROM PurchaseLog WHERE Users_UserID = (
    SELECT UserID FROM Users WHERE UserEmail = "gillj8@cardiff.ac.uk"
  ) AND PurchaseDate = "01/05/2021"
);
