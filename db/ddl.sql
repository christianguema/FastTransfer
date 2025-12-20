CREATE DATABASE fasttransfert_db;
\c fasttransfert_db;
CREATE USER fasttransfert_user WITH PASSWORD 'fast20405';
ALTER ROLE fasttransfert_user LOGIN;
GRANT ALL PRIVILEGES ON DATABASE fasttransfert_db TO fasttransfert_user;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO fasttransfert_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO fasttransfert_user;
ALTER ROLE fasttransfert_user SET client_encoding TO 'utf8';
