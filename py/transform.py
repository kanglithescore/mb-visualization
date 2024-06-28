import pandas as pd
import argparse
import os
from dotenv import load_dotenv

def process_file(file, business_flow):
    print(f"Processing {file}")
    data = pd.read_csv(file)
    data['time'] = pd.to_datetime(data['timestamp'])
    data.dropna(subset=['value'], inplace=True)

    min_value = data['value'].min().round(2)
    avg_value = data['value'].mean().round(2)
    max_value = data['value'].max().round(2)
    start_time = data['time'].min()
    end_time = data['time'].max()
    jurisdiction = data['jurisdiction'].iloc[0]  # Assuming jurisdiction is the same for all rows in the file

    results = {business_flow: {"min": min_value,
                               "avg": avg_value, 
                               "max": max_value, 
                               "start": start_time, 
                               "end": end_time,
                               "jurisdiction": jurisdiction}}
    return results

def main():
    # Load environment variables from a .env file if it exists
    load_dotenv()

    parser = argparse.ArgumentParser(description="Process metrics files for each business flow.")
    parser.add_argument('root_directory', type=str, help='Root directory containing the business flow subdirectories')
    parser.add_argument('--job', type=str, default=os.getenv('JOB', 'load-test-sportsbook-and-casino'), help='Job name')
    parser.add_argument('--run_number', type=str, default=os.getenv('RUNNUMBER', '873'), help='Run number')
    parser.add_argument('--project', type=str, default=os.getenv('PROJECT', 'POC'), help='Project name')
    parser.add_argument('--release', default=False, action="store_true", help="Flag to produce the release output")
    
    args = parser.parse_args()
    
    output_dir = os.path.join(os.path.dirname(args.root_directory), 'transform')  # Save output under the parent "transform" directory
    os.makedirs(output_dir, exist_ok=True)  # Ensure output directory exists
    
    results_list = []
    release_output = []

    # Process each subdirectory
    for business_flow in os.listdir(args.root_directory):
        source_dir = os.path.join(args.root_directory, business_flow)
        
        # Ensure it's a directory
        if os.path.isdir(source_dir):
            print(f"Processing business flow: {business_flow}")

            transactionspersecond_min = None
            transactionspersecond_average = None
            transactionspersecond_max = None
            responsetime_min = None
            responsetime_average = None
            responsetime_max = None
            errorspercent_min = None
            errorspercent_average = None
            errorspercent_max = None
            timetart = None
            timestop = None
            jurisdiction = None

            for file in os.listdir(source_dir):
                if file in ("latency.csv", "request-rate.csv", "error-rate.csv"):
                    csv_file = os.path.join(source_dir, file)
                    results = process_file(csv_file, business_flow)          
                    if file == "request-rate.csv":
                        transactionspersecond_min  = results[business_flow]["min"]
                        transactionspersecond_average = results[business_flow]["avg"]
                        transactionspersecond_max = results[business_flow]["max"]
                        timetart = results[business_flow]["start"]
                        timestop = results[business_flow]["end"]
                        jurisdiction = results[business_flow]["jurisdiction"]
                    if file == "error-rate.csv":
                        errorspercent_min  = results[business_flow]["min"]
                        errorspercent_average = results[business_flow]["avg"]
                        errorspercent_max = results[business_flow]["max"]
                        timetart = results[business_flow]["start"]
                        timestop = results[business_flow]["end"]
                        jurisdiction = results[business_flow]["jurisdiction"]
                    if file == "latency.csv":
                        responsetime_min = results[business_flow]["min"]
                        responsetime_average = results[business_flow]["avg"]
                        responsetime_max = results[business_flow]["max"]
                        timetart = results[business_flow]["start"]
                        timestop = results[business_flow]["end"]
                        jurisdiction = results[business_flow]["jurisdiction"]

            if args.release:
                release_output.append({business_flow: {
                    "avg_requests_rate": transactionspersecond_average,
                    "max_requests_rate": transactionspersecond_max,
                    "avg_latency": responsetime_average,
                    "max_latency": responsetime_max,    
                    "avg_errorspercent": errorspercent_average,
                    "max_errorspercent": errorspercent_max
                }})

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
                'jurisdiction': jurisdiction,
                'cluster': os.getenv('CLUSTER'),
                'environment': os.getenv('ENVIRONMENT', 'PS'),
                'dataset': os.getenv('DATASET'),
                'timetart': timetart,
                'timestop': timestop,
                'ispeak': os.getenv('ISPEAK', 'false'),
                'virtualusers': os.getenv('VIRTUALUSERS'),
                'businessprocess': business_flow,
                'transactionname': os.getenv('TRANSACTIONNAME'),
                'transactionspersecond': transactionspersecond_average,
                'responsetimemin': responsetime_min,
                'responsetimeaverage': responsetime_average,
                'responsetimemax': responsetime_max,
                'errorspercent': errorspercent_average,
                'stepduration': os.getenv('STEPDURATION')
            })

    # Compile all results into one DataFrame
    results_df = pd.DataFrame(results_list)

    # Construct output filename
    output_filename = os.path.join(output_dir, "transform_aggregated_metrics.csv")
    results_df.to_csv(output_filename, index=False)
    print(f"Output saved to {output_filename}")

    if args.release:
        desired_order = ['sportsbook', 'concierge', 'edgebook', 'vegas', 'identity', 'corebook', 'promotions', 'casino', 'scorepay',
                        'placebets', 'validatebets', 'deposits', 'withdrawal', 'cashouttrigger', 'loginpassword', 'loginrefreshtoken']

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
