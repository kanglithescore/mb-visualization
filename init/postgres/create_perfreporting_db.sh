#!/bin/bash

# Create a database named perfreporting owned by perfeng user to store
# the performance test data.

set -e

PERF_PASSWORD="shock"
POSTGRES="psql --username metabase"

# create a shared role to read & write general datasets into postgres perfdb
echo "Creating database role: perfeng"
$POSTGRES <<-EOSQL
CREATE USER perfeng WITH
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
CREATE DATABASE perfreporting OWNER perfeng;
\connect perfreporting;
CREATE TABLE IF NOT EXISTS results (
    id SERIAL PRIMARY KEY,
    job VARCHAR(255),
    runnumber INT DEFAULT NULL,
    project VARCHAR(255),
    product VARCHAR(255),
    release VARCHAR(255),    
    build VARCHAR(255),
    servicebranch VARCHAR(255),
    deploybranch VARCHAR(255),
    testtype VARCHAR(255),
    testname VARCHAR(255),
    testscript VARCHAR(255),
    description TEXT,
    jurisdiction VARCHAR(255),
    cluster VARCHAR(255),
    environment VARCHAR(255),
    dataset VARCHAR(255),
    timetart timestamp,
    timestop timestamp,
    ispeak BOOLEAN,
    virtualusers INT DEFAULT NULL,
    businessprocess VARCHAR(255),
    transactionname VARCHAR(255),
    transactioncount INT DEFAULT NULL,
    transactionspersecond DECIMAL(10,2) DEFAULT NULL,
    responsetimemin DECIMAL(10,2) DEFAULT NULL,
    responsetimeaverage DECIMAL(10,2) DEFAULT NULL,
    responsetimemax DECIMAL(10,2) DEFAULT NULL,
    responsetimemedian DECIMAL(10,2) DEFAULT NULL,
    responsetime90thpercentile DECIMAL(10,2) DEFAULT NULL,
    responsetime95thpercentile DECIMAL(10,2) DEFAULT NULL,
    apdex DECIMAL(10,2) DEFAULT NULL,
    bytesizemin INT DEFAULT NULL,
    bytesizeaverage INT DEFAULT NULL,
    byteizemax INT DEFAULT NULL,
    errorstotal INT DEFAULT NULL,
    errorspercent DECIMAL(10,2) DEFAULT NULL,
    stepduration VARCHAR(255)
);
EOSQL
