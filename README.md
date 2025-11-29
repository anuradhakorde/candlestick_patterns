# DataPatternX

This is a Python project for candlestick pattern detection and visualization using PostgreSQL.

## Docker Setup

- Configure your `.env` file for database connection.
- Run `docker-compose up --build` to start the app and database containers.
- Open virtual environment `source venv/bin/activate`
- Use `python DataPatternX.py` to run analysis and generate charts.

## Local Setup

 - Setup the postgre SQL server in the docker environment
 - Create folder d:/docker_data/progresql
 - run below comand in command prompt/ powershell
 - docker run -d -p 5432:5432 --name postgres-server -e POSTGRES_PASSWORD=loca1databa53 --mount type=bind,source=//d/docker_data/postgresql,target=/var/lib/postgresql/data postgres:latest
 - create Database user for this project and give the access 
 - CREATE USER candlestick_user WITH PASSWORD 'Cand1eStick';
 - CREATE DATABASE candlestick_pattern OWNER candlestick_user;
 - GRANT ALL PRIVILEGES ON DATABASE candlestick_pattern TO candlestick_user;


## Folder Structure

Refer to project documentation for folder and module details.
