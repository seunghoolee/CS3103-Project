DELIMITER //
DROP PROCEDURE IF EXISTS dropUser //

CREATE PROCEDURE dropUser(IN id INT)
begin
	DELETE FROM users WHERE userID = id;
end//
DELIMITER ;
