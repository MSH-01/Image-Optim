CREATE SCHEMA IF NOT EXISTS imageoptimteam10;
USE imageoptimteam10;
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
  `PromoCodes_PromoID` INT,
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
