# Running Metabase in Docker

Running Metabase and PostgresSQL in the containers.

Docker compose on start will create two database in PostgresSQL: one storing for Metabase data and one for performance data.

Set your DB crendetials accordingly in /init/postgres/create_metabase_db.sh and create_perfreporting_db.sh

## Instructions

- make up (start)
- make down (stop)

## Note

You will need to add performance database via metabase UI
