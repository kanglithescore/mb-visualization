#!/bin/bash

# Create metabase database owned by metabase user to store
# metabase application data such users, dashboard and etc.

set -e # exit if a command exits with a not-zero exit code

METABASE_PASSWORD="metabase"
POSTGRES="psql --username postgres"

# create a shared role to read & write general datasets into postgres metabase db
echo "Creating database role: metabase"
$POSTGRES <<-EOSQL
CREATE USER metabase WITH
    LOGIN
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE
    NOINHERIT
    NOREPLICATION
    PASSWORD '$METABASE_PASSWORD';
EOSQL

# create database
echo "Creating database: metabase"
$POSTGRES <<EOSQL
CREATE DATABASE metabase OWNER metabase;
EOSQL
