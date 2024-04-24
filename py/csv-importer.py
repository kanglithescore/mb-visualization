"""
Transaction data in a CSV tile to Metabase PostgreSQL DB.

This script processes a directory which contains the CSV file with transaction data and writes it to a PostgreSQL database in Metabase.

Usage:
    python script_name.py <directory>

Parameters:
    csv_file (str): The directory to the CSV file containing transaction data.

Environment Variables:
    METABASE_HOST (str): The hostname of the Metabase RDS PostgreSQL database. If not set, the default value is used.
    METABASE_USER (str): The username for connecting to the Metabase PostgreSQL database.
    METABASE_PASSWORD (str): The password for connecting to the Metabase PostgreSQL database.
    METABASE_DB (str): The name of the Metabase PostgreSQL database.
    METABASE_PORT (str): The port number for connecting to the Metabase PostgreSQL database.

Functions:
    - read_csv_and_write_to_db(csv_file: str): Reads transaction data from a CSV file and writes it to the Metabase PostgreSQL database.
    - write_transaction_metabase(txn_summary: dict): Writes transaction summary metrics to the Metabase PostgreSQL database.

Example:
    python script_name.py directory
"""

import argparse
import csv
import os
import time

import psycopg2

# The globle environment variables
METABASE_HOST = os.getenv("METABASE_HOST", default="localhost")
METABASE_USER = "perfeng"
METABASE_PASSWORD = "shock"
METABASE_DB = "perfreporting"
METABASE_PORT = "5432"


def read_csv_and_write_to_db(csv_file: str):
    """Read transaction data from a CSV file and write it to a PostgreSQL database."""
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            write_transaction_metabase(row)


def write_transaction_metabase(txn_summary: dict):
    """Write transaction summary metric to metabase postgresql database."""
    try:
        time.sleep(1)
        print(f"Metabase RDS PostgreSQL host name is: {METABASE_HOST}")
        connection = psycopg2.connect(user=METABASE_USER, password=METABASE_PASSWORD, host=METABASE_HOST, port=METABASE_PORT, database=METABASE_DB)
        cursor = connection.cursor()

        key = ", ".join(txn_summary.keys())
        position = ", ".join(['%s'] * len(txn_summary))

        # insert given transaction metrics into the metabase
        insert_query = "INSERT INTO results (%s) VALUES (%s)" % (key, position)
        cursor.execute(insert_query, list(txn_summary.values()))
        connection.commit()

        print(f"Transaction [{txn_summary.get('transactionname')}] metrics inserted to the Metabase successfully")
    except (Exception, psycopg2.Error) as e:
        print(f"Error while connecting to Metabase PostgreSQL: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Metabase PostgreSQL connection is closed")


def process_directory(directory: str):
    """Process each CSV file in the specified directory."""
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            csv_file = os.path.join(directory, filename)
            print(f"Processing file: {csv_file}")
            read_csv_and_write_to_db(csv_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process CSV files contained in a directory and write to Metabase DB.')
    parser.add_argument('directory', type=str, help='The directory containing CSV files to process.')
    args = parser.parse_args()

    process_directory(args.directory)