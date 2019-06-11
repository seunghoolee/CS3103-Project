DELIMITER //
DROP PROCEDURE IF EXISTS checkIfUserIsThere//

CREATE PROCEDURE checkIfUserIsThere(IN name VARCHAR(50))
begin
SELECT * FROM users WHERE userName = name;
end//
DELIMITER ;
