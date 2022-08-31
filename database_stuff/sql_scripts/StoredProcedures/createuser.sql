DELIMITER //
CREATE DEFINER=`root`@`localhost` PROCEDURE `CreateUser`(IN p_UserEmail VARCHAR(45), IN p_UserPassword VARCHAR(45), IN p_CompanyName VARCHAR(45), IN p_ContactName VARCHAR(45), IN p_CompanyAddress VARCHAR(45), IN p_Countries_CountryID INT, IN p_CompanyTypes_SizeID INT)
BEGIN
	INSERT INTO users (UserEmail, UserPassword, CompanyName, ContactName, CompanyAddress,Countries_CountryID, CompanyTypes_SizeID) VALUES (p_UserEmail, p_UserPassword, p_CompanyName, p_ContactName, p_CompanyAddress,p_Countries_CountryID, p_CompanyTypes_SizeID);
END