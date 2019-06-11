DELIMITER //
DROP PROCEDURE IF EXISTS addUser //

CREATE PROCEDURE addUser(IN userName VARCHAR(50))
begin
	INSERT into users (userName) values (userName);
end//
DELIMITER ;
