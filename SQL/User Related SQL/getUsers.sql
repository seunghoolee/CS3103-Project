DELIMITER //
DROP PROCEDURE IF EXISTS getUser //

CREATE PROCEDURE getUsers()
begin
  SELECT * FROM users;
end//
DELIMITER ;
