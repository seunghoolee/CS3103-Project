DELIMITER //
DROP PROCEDURE IF EXISTS getToDoItem //

CREATE PROCEDURE getToDoItem()
begin
  SELECT * FROM toDoList;
end//
DELIMITER ;
