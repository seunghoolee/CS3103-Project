DELIMITER //
DROP PROCEDURE IF EXISTS getUserByID //

CREATE PROCEDURE getUserByID(IN id INT)
begin
  SELECT *
	FROM users WHERE userID = id;
end//
DELIMITER ;
