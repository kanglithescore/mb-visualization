#!/bin/bash

# Create metabase database named perfreporting owned by metabase user to store
# the performance test data.

set -e

PERF_PASSWORD="epDbPassword"
POSTGRES="psql --username postgres"

# create a shared role to read & write general datasets into postgres perfdb
echo "Creating database role: epdbuser"
$POSTGRES <<-EOSQL
CREATE USER epdbuser WITH
    LOGIN
    SUPERUSER
    CREATEDB
    CREATEROLE
    INHERIT
    REPLICATION
    PASSWORD '$PERF_PASSWORD';
EOSQL

# create database
echo "Creating database: perfreporting"
$POSTGRES <<-EOSQL
CREATE DATABASE perfreporting OWNER epdbuser;
\connect perfreporting;
CREATE TABLE IF NOT EXISTS jmeterResults (
    id SERIAL PRIMARY KEY,
    job VARCHAR(255),
    runnumber INT,
    project VARCHAR(255),
    product VARCHAR(255),
    build VARCHAR(255),
    productbranch VARCHAR(255),
    deploybranch VARCHAR(255),
    dockerbranch VARCHAR(255),
    testtype VARCHAR(255),
    testname VARCHAR(255),
    description TEXT,
    jurisdiction VARCHAR(255),
    cluster VARCHAR(255),
    environment VARCHAR(255),
    dataset VARCHAR(255),
    timetart timestamp,
    timestop timestamp,
    ispeak BOOLEAN,
    virtualusers INT,
    businessprocess VARCHAR(255),
    transactionname VARCHAR(255),
    transactioncount INT,
    transactionspersecond DECIMAL(10,2),
    responsetimemin DECIMAL(10,2),
    responsetimeaverage DECIMAL(10,2),
    responsetimemax DECIMAL(10,2),
    responsetimemedian DECIMAL(10,2),
    responsetime90thpercentile DECIMAL(10,2),
    responsetime95thpercentile DECIMAL(10,2),
    apdex DECIMAL(10,2),
    bytesizemin INT,
    bytesizeaverage INT,
    byteizemax INT,
    errorstotal INT,
    errorspercent DECIMAL(10,2),
    stepduration VARCHAR(255)
);
EOSQL
