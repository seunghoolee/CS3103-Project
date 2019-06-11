DROP TABLE IF EXISTS toDoList;

CREATE TABLE toDoList(
   toDoListID  INT   NOT NULL AUTO_INCREMENT,
   toDoItem    varchar(50) NOT NULL,
   userID INT,
   PRIMARY KEY (toDoListID),
   FOREIGN KEY (userID)
     REFERENCES users(userID)
	ON DELETE CASCADE
	ON UPDATE CASCADE
);