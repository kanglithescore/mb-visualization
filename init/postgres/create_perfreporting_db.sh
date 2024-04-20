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
    runNumber INT,
    timeStart timestamp,
    timeStop timestamp,
    product VARCHAR(255),
    productBranch VARCHAR(255),
    deployBranch VARCHAR(255),
    dockerBranch VARCHAR(255),
    testType VARCHAR(255),
    testName VARCHAR(255),
    transactionName VARCHAR(255),
    environment VARCHAR(255),
    build VARCHAR(255),
    dataset VARCHAR(255),
    description TEXT,
    isPeak BOOLEAN,
    virtualUsers INT,
    transactionCount INT,
    transactionsPerSecond DECIMAL(10,2),
    responseTimeMin INT,
    responseTimeAverage INT,
    responseTimeMax INT,
    responseTimeMedian INT,
    responseTime90thPercentile INT,
    responseTime95thPercentile INT,
    apdex DECIMAL(10,2),
    byteSizeMin INT,
    byteSizeAverage INT,
    byteSizeMax INT,
    errorsTotal INT,
    errorsPercent DECIMAL(10,2),
    project VARCHAR(255),
    stepDuration VARCHAR(255)
);
EOSQL
