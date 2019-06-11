DELIMITER //
DROP PROCEDURE IF EXISTS getOneUser //

CREATE PROCEDURE getOneUser(IN name VARCHAR(50))
begin
  SELECT userID
	FROM users WHERE userName = name;
end//
DELIMITER ;
