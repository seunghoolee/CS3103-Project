DELIMITER //
DROP PROCEDURE IF EXISTS getSpecificItem //

CREATE PROCEDURE getSpecificItem(IN id INT)
begin
  SELECT * FROM toDoList WHERE userID = id;
end//
DELIMITER ;
