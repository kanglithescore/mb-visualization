import pandas as pd
import argparse
import os
from dotenv import load_dotenv

def process_files(rate_file, avg_file, p95_file, output_filename, business_flow, job, run_number, project):
    # Read files
    rate_data = pd.read_csv(rate_file)
    avg_latency_data = pd.read_csv(avg_file)
    p95_latency_data = pd.read_csv(p95_file)
    
    # Clean and prepare the data
    rate_data['time'] = pd.to_datetime(rate_data['time'])
    avg_latency_data['time'] = pd.to_datetime(avg_latency_data['time'])
    p95_latency_data['time'] = pd.to_datetime(p95_latency_data['time'])
    
    rate_data.dropna(subset=['value'], inplace=True)
    avg_latency_data.dropna(subset=['value'], inplace=True)
    p95_latency_data.dropna(subset=['value'], inplace=True)

    # Strip 'jurisdiction:' from the 'group' column in all dataframes
    rate_data['group'] = rate_data['group'].str.replace('jurisdiction:', '')
    avg_latency_data['group'] = avg_latency_data['group'].str.replace('jurisdiction:', '')
    p95_latency_data['group'] = p95_latency_data['group'].str.replace('jurisdiction:', '')
    
    # Calculate averages
    avg_request_rate = rate_data.groupby('group')['value'].mean().round(2)
    avg_latency = (avg_latency_data.groupby('group')['value'].mean() * 1000).astype(int)
    avg_p95_latency = (p95_latency_data.groupby('group')['value'].mean() * 1000).astype(int)
    
    # Determine start and end times
    start_time = rate_data.groupby('group')['time'].min()
    end_time = rate_data.groupby('group')['time'].max()
    
    # Combine all results into one DataFrame
    results = pd.DataFrame({
        'Jurisdiction': avg_request_rate.index,
        'Request Rate': avg_request_rate.values,
        'Average Latency (ms)': avg_latency.values,
        'P95 Latency (ms)': avg_p95_latency.values,
        'Start Time': start_time.values,
        'End Time': end_time.values,
        'Business Flow': business_flow,
        'Job': job,
        'Run Number': run_number,
        'Project': project
    })

    # Save to CSV with business flow name as prefix
    results.to_csv(output_filename, index=False)

def main():
    # Load environment variables from a .env file if it exists
    load_dotenv()

    parser = argparse.ArgumentParser(description="Process metrics files for each business flow.")
    parser.add_argument('root_directory', type=str, help='Root directory containing the business flow subdirectories')
    parser.add_argument('--job', type=str, default=os.getenv('JOB', 'load-test-sportsbook-and-casino'), help='Job name')
    parser.add_argument('--run_number', type=str, default=os.getenv('RUNNUMBER', '873'), help='Run number')
    parser.add_argument('--project', type=str, default=os.getenv('PROJECT', 'POC'), help='Project name')
    
    args = parser.parse_args()
    
    # Process each subdirectory
    for business_flow in os.listdir(args.root_directory):
        subdirectory_path = os.path.join(args.root_directory, business_flow)
        
        # Ensure it's a directory
        if os.path.isdir(subdirectory_path):
            rate_file = os.path.join(subdirectory_path, 'rate.csv')
            avg_file = os.path.join(subdirectory_path, 'avg.csv')
            p95_file = os.path.join(subdirectory_path, 'p95.csv')
            output_filename = os.path.join(args.root_directory, f"{business_flow}_output_metrics.csv")
            
            # Process files in each business flow directory
            process_files(rate_file, avg_file, p95_file, output_filename, business_flow, args.job, args.run_number, args.project)
            print(f"Processed files for business flow: {business_flow}")

if __name__ == "__main__":
    main()
