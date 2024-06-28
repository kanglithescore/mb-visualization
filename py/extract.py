import json
import os
import argparse
from datadog import initialize, api
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd

# Initialize Datadog API keys from environment variables
options = {
    'api_key': os.getenv('DATADOG_API_KEY'),
    'app_key': os.getenv('DATADOG_APP_KEY')
}
initialize(**options)

# Load queries from JSON configuration file
def load_queries(config_file):
    with open(config_file, 'r') as file:
        config = json.load(file)
    return config['queries']

# Function to extract data for a given query
def extract(query, start_at, end_at, time_delta, jurisdiction, default_timestamps=None):
    print(f'Running extraction for query: {query["metric"]}')

    datetime_list = []
    value_list = []
    metric_list = []

    iteration_start = start_at

    while iteration_start < end_at:
        iteration_end = min(iteration_start + time_delta, end_at)
        results = api.Metric.query(start=iteration_start, end=iteration_end, query=query["query"])
        for datadog_result in results['series']:
            for time_value_pair_list in datadog_result['pointlist']:
                timestamp = time_value_pair_list[0] / 1000
                converted_datetime = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                datetime_list.append(converted_datetime)
                if query["metric"].startswith("latency"):
                    value_list.append(time_value_pair_list[1] * 1000)  # Convert to milliseconds
                else:
                    value_list.append(time_value_pair_list[1])
                metric_list.append(datadog_result['metric'])

        iteration_start = iteration_end

    if not datetime_list and default_timestamps is not None:
        datetime_list = default_timestamps
        # In case no value from the response
        value_list = [0] * len(default_timestamps)
        jurisdiction_list = [jurisdiction] * len(default_timestamps)
    else:
        jurisdiction_list = [jurisdiction] * len(datetime_list)

    all_data = {
        'timestamp': datetime_list,
        'value': value_list,
        'jurisdiction': jurisdiction_list
    }

    print(f'Finished extraction for query: {query["metric"]}')
    return pd.DataFrame.from_dict(all_data)

# Function to calculate error rate
def calculate_error_rate(error_df, hits_df, jurisdiction):
    # Merge the data frames on timestamp, treating missing error values as 0
    merged_df = pd.merge(hits_df, error_df, on='timestamp', how='left', suffixes=('_hits', '_error'))
    merged_df['value_error'] = merged_df['value_error'].fillna(0)  # Fill NaNs in the error values with 0

    # Calculate the error rate
    merged_df['value'] = (merged_df['value_error'] / merged_df['value_hits'] * 100).round(2)
    merged_df['jurisdiction'] = jurisdiction

    return merged_df[['timestamp', 'value', 'jurisdiction']]

# Main function to run all queries and perform calculations
def run_queries(queries, start, end, time_delta):
    data_frames = {}
    jurisdiction = ""
    
    # Create a root directory based on the current date
    today = datetime.now().strftime('%Y%m%d')
    root_dir = os.path.join(today, 'extract')

    # Default timestamps to ensure consistency
    default_timestamps = None

    for query in queries:
        if "jurisdiction" in query:
            jurisdiction = query.get("jurisdiction")
        
        category_dir = query['category']
        category_dir = os.path.join(root_dir, category_dir)
        if not os.path.exists(category_dir):
            os.makedirs(category_dir)
        
        data_metrics = extract(query, start, end, time_delta, jurisdiction, default_timestamps)
        
        if default_timestamps is None:
            default_timestamps = data_metrics['timestamp'].tolist()
        
        csv_file_name = f"{category_dir}/{query['metric']}.csv"
        data_metrics.to_csv(csv_file_name, index=False)
        print(f"Data has been written to {csv_file_name}")
        
        data_frames[f"{query['category']}-{query['metric']}"] = data_metrics

    for category in set([query['category'] for query in queries]):
        if f"{category}-request-error" in data_frames and f"{category}-request-hits" in data_frames:
            error_rate_df = calculate_error_rate(data_frames[f"{category}-request-error"], data_frames[f"{category}-request-hits"], jurisdiction)
            error_rate_csv_file_name = f"{category}/error-rate.csv"
            error_file = os.path.join(root_dir, error_rate_csv_file_name)
            error_rate_df.to_csv(error_file, index=False)
            print(f"Error rate data has been written to {error_rate_csv_file_name}")

# Argument parser for command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Datadog Metrics Extractor")
    parser.add_argument('--start', type=int, required=True, help='Start time in epoch format')
    parser.add_argument('--end', type=int, required=True, help='End time in epoch format')
    parser.add_argument('--time_delta', type=int, default=600, help='Time delta in seconds (default: 600)')
    parser.add_argument('--config', type=str, default='queries.json', help='Path to JSON configuration file (default: queries.json)')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    queries = load_queries(args.config)
    run_queries(queries, args.start, args.end, args.time_delta)
