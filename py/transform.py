"""
Transform Datadog Metrics Data.

This script processes a directory which contains subdirectories with CSV files of Datadog raw metrics data from extract.py
It calculates min, average, and max values for each metric, and compiles the results into a summary CSV file.
Optionally, it can produce a release output based on specific flags.

Usage:
    python transform.py <root_directory> 
    python transform.py <root_directory> --release

Parameters:
    root_directory (str): The root directory containing the business flow subdirectories with CSV files.

Environment Variables:
    JOB (str): The job name. Default is 'load-test-sportsbook-and-casino'.
    RUNNUMBER (str): The run number. Default is '001'.
    PROJECT (str): The project name. Default is 'POC'.
    PRODUCT (str): The product name.
    RELEASE (str): The release version.
    BUILD (str): The build version.
    SERVICEBRANCH (str): The service branch.
    DEPLOYBRANCH (str): The deploy branch.
    TESTTYPE (str): The test type.
    TESTNAME (str): The test name.
    TESTSCRIPT (str): The test script.
    DESCRIPTION (str): The description.
    CLUSTER (str): The cluster.
    ENVIRONMENT (str): The environment. Default is 'PS'.
    DATASET (str): The dataset.
    ISPEAK (str): Indicates if it's a peak. Default is 'false'.
    VIRTUALUSERS (str): The number of virtual users.
    TRANSACTIONNAME (str): The transaction name.
    STEPDURATION (str): The step duration.

Functions:
    - process_file(file: str): Processes a single CSV file to calculate min, avg, max values and get time range.
    - process_directory(directory_path: str, business_flow: str): Processes all relevant CSV files in a directory for a given business flow.
    - main(): Main function to process metrics files for each business flow and compile results.

Example:
    python transform.py root_directory
"""

import pandas as pd
import argparse
import os
from dotenv import load_dotenv

def process_file(file):
    """Process a single CSV file to calculate min, avg, max values and get time range."""
    print(f"Processing {file}")
    data = pd.read_csv(file)
    data['time'] = pd.to_datetime(data['timestamp'])
    data.dropna(subset=['value'], inplace=True)

    min_value = data['value'].min().round(2)
    avg_value = data['value'].mean().round(2)
    max_value = data['value'].max().round(2)
    start_time = data['time'].min()
    end_time = data['time'].max()
     # Assuming jurisdiction is the same for all rows in the file
    jurisdiction = data['jurisdiction'].iloc[0]

    return {
        "min": min_value,
        "avg": avg_value,
        "max": max_value,
        "start": start_time,
        "end": end_time,
        "jurisdiction": jurisdiction
    }

def process_directory(directory_path, category):
    """ Process all relevant CSV files in a directory for a given category."""
    metrics = {
        "request-rate.csv": None,
        "latency.csv": None,
        "error-rate.csv": None
    }

    for file in os.listdir(directory_path):
        if file in metrics:
            file_path = os.path.join(directory_path, file)
            metrics[file] = process_file(file_path)

    return metrics

def main():
    """Main fucntion."""
    # Load environment variables from a .env file if it exists
    load_dotenv()

    parser = argparse.ArgumentParser(description="Process metrics files for each business flow.")
    parser.add_argument('root_directory', type=str, help='Root directory containing the business flow subdirectories')
    parser.add_argument('--job', type=str, default=os.getenv('JOB', 'load-test-sportsbook-and-casino'), help='Job name')
    parser.add_argument('--run_number', type=str, default=os.getenv('RUNNUMBER', '0'), help='Run number')
    parser.add_argument('--project', type=str, default=os.getenv('PROJECT', 'Dummy'), help='Project name')
    parser.add_argument('--release', default=False, action="store_true", help="Flag to produce the release output")
    
    args = parser.parse_args()
    # Save output under the parent "transform" directory
    output_dir = os.path.join(os.path.dirname(args.root_directory), 'transform')
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # A list to insert to the database
    results_list = []
    # A list values to get printed out in console to copy and paste for Release testing 
    release_output = []

    # Process each subdirectory
    for category in os.listdir(args.root_directory):
        source_dir = os.path.join(args.root_directory, category)
        
        # Ensure it's a directory
        if os.path.isdir(source_dir):
            print(f"Processing category: {category}")
            metrics = process_directory(source_dir, category)

            if metrics["request-rate.csv"]:
                request_rate = metrics["request-rate.csv"]
            else:
                request_rate = {"min": None, "avg": None, "max": None, "start": None, "end": None, "jurisdiction": None}

            if metrics["latency.csv"]:
                latency = metrics["latency.csv"]
            else:
                latency = {"min": None, "avg": None, "max": None, "start": None, "end": None, "jurisdiction": None}

            if metrics["error-rate.csv"]:
                error_rate = metrics["error-rate.csv"]
            else:
                error_rate = {"min": None, "avg": None, "max": None, "start": None, "end": None, "jurisdiction": None}

            if args.release:
                release_output.append({
                    category: {
                        "avg_requests_rate": request_rate["avg"],
                        "max_requests_rate": request_rate["max"],
                        "avg_latency": latency["avg"],
                        "max_latency": latency["max"],
                        "avg_errorspercent": error_rate["avg"],
                        "max_errorspercent": error_rate["max"]
                    }
                })

            results_list.append({
                'job': args.job,
                'runnumber': args.run_number,
                'project': args.project,
                'product': os.getenv('PRODUCT'),
                'release': os.getenv('RELEASE'),
                'build': os.getenv('BUILD'),
                'servicebranch': os.getenv('SERVICEBRANCH'),
                'deploybranch': os.getenv('DEPLOYBRANCH'),
                'testtype': os.getenv('TESTTYPE'),
                'testname': os.getenv('TESTNAME'),
                'testscript': os.getenv('TESTSCRIPT'),
                'description': os.getenv('DESCRIPTION'),
                'jurisdiction': request_rate["jurisdiction"] or latency["jurisdiction"] or error_rate["jurisdiction"],
                'cluster': os.getenv('CLUSTER'),
                'environment': os.getenv('ENVIRONMENT', 'ps'),
                'dataset': os.getenv('DATASET'),
                'timetart': request_rate["start"] or latency["start"] or error_rate["start"],
                'timestop': request_rate["end"] or latency["end"] or error_rate["end"],
                'ispeak': os.getenv('ISPEAK', 'false'),
                'virtualusers': os.getenv('VIRTUALUSERS'),
                'businessprocess': category,
                'transactionname': os.getenv('TRANSACTIONNAME'),
                'transactionspersecond': request_rate["avg"],
                'responsetimemin': latency["min"],
                'responsetimeaverage': latency["avg"],
                'responsetimemax': latency["max"],
                'errorspercent': error_rate["avg"],
                'stepduration': os.getenv('STEPDURATION')
            })

    # Compile all results into one DataFrame
    results_df = pd.DataFrame(results_list)

    # Construct output filename
    output_filename = os.path.join(output_dir, "transform_aggregated_metrics.csv")
    results_df.to_csv(output_filename, index=False)
    print(f"Output saved to {output_filename}")

    # Print out the values to copy it to release excel in the specific desired order
    if args.release:
        desired_order = [
            'sportsbook', 'concierge', 'edgebook', 'vegas', 'identity', 'corebook', 'promotions', 'casino', 'scorepay',
            'placebets', 'validatebets', 'deposits', 'withdrawal', 'cashouttrigger', 'loginpassword', 'loginrefreshtoken'
        ]

        # Custom sort key function
        def sort_key(item):
            key = list(item.keys())[0]
            if key in desired_order:
                return desired_order.index(key)
            return len(desired_order)

        # Sort the list
        sorted_data = sorted(release_output, key=sort_key)
        # Extract the values and flatten them
        flattened_values = [value for item in sorted_data for sub_dict in item.values() for value in sub_dict.values()]

        # Join the values with commas
        result = ', '.join(map(str, flattened_values))
        print(result)

if __name__ == "__main__":
    main()
