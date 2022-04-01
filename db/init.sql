--
--  Initialization schema for database App
-- ---------------------------------------------

CREATE DATABASE IF NOT EXISTS App;
GRANT ALL PRIVILEGES
    ON App.*
    TO 'app'@'localhost'
    IDENTIFIED BY 'app';
