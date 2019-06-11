DELIMITER //
DROP PROCEDURE IF EXISTS getSpecificItemFromUser //

CREATE PROCEDURE getSpecificItemFromUser(IN toDoid INT, IN idofUser INT)
begin
  SELECT * FROM toDoList WHERE toDoListID = toDoid AND userID = idofUser;
end//
DELIMITER ;
