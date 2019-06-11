DELIMITER //
DROP PROCEDURE IF EXISTS dropStuffToDo //

CREATE PROCEDURE dropStuffToDo(IN toDoid INT, IN idofUser INT)
begin
	DELETE FROM toDoList WHERE toDoListID = toDoid AND userID = idofUser;
end//
DELIMITER ;
