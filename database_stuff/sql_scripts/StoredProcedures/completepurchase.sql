DELIMITER //
CREATE DEFINER=`root`@`localhost` PROCEDURE `CompletePurchase`(IN p_PurchasePrice double,IN p_PurchaseDate varchar(45), IN p_Products_ProductID int, IN p_Licenses_LicenseID int, IN p_CompanyTypes_SizeID int, IN p_Users_UserID int, IN p_PromoCodes_PromoID int)
BEGIN
	INSERT INTO purchaselog (PurchasePrice, PurchaseDate, Products_ProductID, Licenses_LicenseID, CompanyTypes_SizeID, Users_UserID,PromoCodes_PromoID) VALUES (p_PurchasePrice, p_PurchaseDate, p_Products_ProductID, p_Licenses_LicenseID, p_CompanyTypes_SizeID, p_Users_UserID, p_PromoCodes_PromoID);
END;
