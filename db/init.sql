CREATE DATABASE habits;
CREATE USER habits_user WITH PASSWORD '91z5sr91z5SR!';
GRANT ALL PRIVILEGES ON DATABASE habits TO habits_user;
ALTER DATABASE habits OWNER TO habits_user;