DELIMITER //
DROP PROCEDURE IF EXISTS addStuffToDo //

CREATE PROCEDURE addStuffToDo(IN toDoItem VARCHAR(50))
begin
	INSERT INTO toDoList(toDoItem) VALUES (toDoItem);
end//
DELIMITER ;