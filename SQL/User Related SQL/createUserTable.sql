DROP TABLE IF EXISTS users;

CREATE TABLE users(
   userID  INT   NOT NULL AUTO_INCREMENT,
   userName    varchar(50) NOT NULL,
   PRIMARY KEY (userID, userName)
);
