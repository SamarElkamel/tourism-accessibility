-- init.sql
CREATE USER IF NOT EXISTS 'appuser'@'%' IDENTIFIED BY 'apppassword';
GRANT ALL PRIVILEGES ON tourismdb.* TO 'appuser'@'%';
FLUSH PRIVILEGES;