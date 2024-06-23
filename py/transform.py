import pandas as pd
import argparse
import os
from dotenv import load_dotenv

def process_files(source_directory, output_directory, business_flow, job, run_number, project):
    # Iterate over all CSV files in the directory
    for file in os.listdir(source_directory):
        if file.endswith('.csv'):
            csv_file = os.path.join(source_directory, file)
            print(f"Processing {csv_file}")
            data = pd.read_csv(csv_file)
            data['time'] = pd.to_datetime(data['timestamp'])
            data.dropna(subset=['value'], inplace=True)
            data['jurisdiction'] = data['jurisdiction'].str.replace('jurisdiction:', '')

            avg_value = data.groupby('jurisdiction')['value'].mean().round(2)
            start_time = data.groupby('jurisdiction')['time'].min()
            end_time = data.groupby('jurisdiction')['time'].max()

            # Compile results into DataFrame
            results = pd.DataFrame({
                'job': job,
                'run_number': run_number,
                'project': project,
                'business_flow': business_flow,
                'jurisdiction': avg_value.index,
                'start_time': start_time.values,
                'end_time': end_time.values,
                'average_value': avg_value.values,
            })

            # Construct output filename based on business flow and the original file
            output_filename = f"{business_flow}_{file[:-4]}_output.csv"
            results.to_csv(os.path.join(output_directory, output_filename), index=False)
            print(f"Output saved to {output_filename}")

def main():
    # Load environment variables from a .env file if it exists
    load_dotenv()

    parser = argparse.ArgumentParser(description="Process metrics files for each business flow.")
    parser.add_argument('root_directory', type=str, help='Root directory containing the business flow subdirectories')
    parser.add_argument('--job', type=str, default=os.getenv('JOB', 'load-test-sportsbook-and-casino'), help='Job name')
    parser.add_argument('--run_number', type=str, default=os.getenv('RUNNUMBER', '873'), help='Run number')
    parser.add_argument('--project', type=str, default=os.getenv('PROJECT', 'POC'), help='Project name')
    
    args = parser.parse_args()
    
    output_dir = os.path.join(os.path.dirname(args.root_directory), 'transform')  # Save output under the parent "transform" directory
    os.makedirs(output_dir, exist_ok=True)  # Ensure output directory exists

    # Process each subdirectory
    for business_flow in os.listdir(args.root_directory):
        source_dir = os.path.join(args.root_directory, business_flow)
        
        # Ensure it's a directory
        if os.path.isdir(source_dir):
            print(f"Processing business flow: {business_flow}")
            process_files(source_dir, output_dir, business_flow, args.job, args.run_number, args.project)

if __name__ == "__main__":
    main()
