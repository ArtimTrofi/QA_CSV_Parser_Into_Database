import argparse
import pandas as pd
from pymongo import MongoClient
import csv
import re
from datetime import datetime
from datetime import timedelta

client = MongoClient('mongodb://localhost:27017/')
db = client['qa_reports_db']
#------------------------------------------------------------------------------------------------------------------------------------
#MongoDB Collection 1
def parse_csv_to_collection_1(file_path):
    collection = db['collection_1']
    try:
        data = pd.read_excel(file_path, engine='openpyxl')

        records = data.to_dict(orient='records')

        collection.insert_many(records)
        print(f"Data from {file_path} has been inserted into Collection 1.")
    except Exception as e:
        print(f"An error occurred: {e}")
    pass
#------------------------------------------------------------------------------------------------------------------------------------
#MongoDB Collection 2
def parse_csv_to_collection_2(file_path):
    collection = db['collection_2']
    try:
        data = pd.read_excel(file_path, engine='openpyxl')

        data['Build #'].fillna('Unknown', inplace=True)

        records = data.to_dict(orient='records')

        collection.insert_many(records)
        print(f"Data from {file_path} has been inserted into Collection 2.")
    except Exception as e:
        print(f"An error occurred: {e}")
    pass
#------------------------------------------------------------------------------------------------------------------------------------
#work done user
def list_work_by_user_to_csv(user, output_file):
    collection_1 = db['collection_1']
    collection_2 = db['collection_2']
    try:
        print(f"Searching for work done by {user}...")
        work_1 = list(collection_1.find({'Test Owner': user}))
        work_2 = list(collection_2.find({'Test Owner': user}))

        # Combine and deduplicate using a dictionary.
        combined_work = {}
        for work in work_1 + work_2:
            combined_work[(work['Test Owner'], work['Test Case'], work.get('Build #', 'No Build'))] = work
        
        # Create a list
        deduplicated_work = list(combined_work.values())

        # pandas DataFrame for better formatting
        df = pd.DataFrame(deduplicated_work)

        if '_id' in df.columns:
            df.drop('_id', axis=1, inplace=True)

        df.sort_values(by='Build #', inplace=True)

        df.to_csv(output_file, index=False)
        print(f"Work by {user} has been written to {output_file}")

    except Exception as e:
        print(f"An error occurred while exporting work by {user} to CSV: {e}")
    pass
#------------------------------------------------------------------------------------------------------------------------------------
#repeatable bugs
def export_repeatable_bugs_to_csv(output_file):
    collection_1 = db['collection_1']
    collection_2 = db['collection_2']
    try:
        yes_regex = re.compile('^yes$', re.IGNORECASE)

        repeatable_2 = { 
            (bug['Test Case'], bug['Test Owner']): bug 
            for bug in collection_2.find({'Repeatable?': {'$regex': yes_regex}})
        }
        #from collection1 if they don't exist in 2
        repeatable_1 = collection_1.find({'Repeatable?': {'$regex': yes_regex}})
        for bug in repeatable_1:
            key = (bug['Test Case'], bug['Test Owner'])
            if key not in repeatable_2:
                repeatable_2[key] = bug

        df = pd.DataFrame(list(repeatable_2.values()))

        if '_id' in df.columns:
            df.drop('_id', axis=1, inplace=True)

        df.to_csv(output_file, index=False)
        print(f"Exported repeatable bugs to {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")
    pass
#------------------------------------------------------------------------------------------------------------------------------------
#blockers
def export_blocker_bugs_to_csv(output_file):
    collection_1 = db['collection_1']
    collection_2 = db['collection_2']
    try:
        yes_regex = re.compile('^yes$', re.IGNORECASE)
        unique_blocker_bugs = {}
        
        #collection  2
        for bug in collection_2.find({'Blocker?': {'$regex': yes_regex}}):
            unique_key = (bug['Test Case'], bug['Test Owner'])
            unique_blocker_bugs[unique_key] = bug
        
        #from collection1 if they don't exist in 2
        for bug in collection_1.find({'Blocker?': {'$regex': yes_regex}}):
            unique_key = (bug['Test Case'], bug['Test Owner'])
            if unique_key not in unique_blocker_bugs:
                unique_blocker_bugs[unique_key] = bug
        
        df = pd.DataFrame(list(unique_blocker_bugs.values()))
        
        if '_id' in df.columns:
            df.drop(columns=['_id'], inplace=True)
        
        df.to_csv(output_file, index=False)
        print(f"Exported blocker bugs to {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")


    pass
#------------------------------------------------------------------------------------------------------------------------------------
#specific build date
def export_reports_by_build_to_csv(build_date_str, output_file):
    collection = db['collection_2']
    build_date = datetime.strptime(build_date_str, '%m/%d/%Y')
    #PIPELINE!!!
    try:
        pipeline = [
            {
                '$match': {
                    'Build #': {
                        '$gte': build_date,
                        '$lt': build_date + timedelta(days=1)
                    }
                }
            }
        ]

        reports = list(collection.aggregate(pipeline))
        print(f"Found {len(reports)} reports for build date {build_date_str}.")

        if reports:
            df = pd.DataFrame(reports)

            if '_id' in df.columns:
                df = df.drop('_id', axis=1)

            df.to_csv(output_file, index=False)
            print(f"Exported reports to '{output_file}'.")
        else:
            print("No data to write to CSV.")

    except Exception as e:
        print(f"An error occurred: {e}")

    pass
#------------------------------------------------------------------------------------------------------------------------------------
def report_test_cases(output_file):
    collection = db['collection_2']
    try:
        first_entry = collection.find().sort('_id', 1).limit(1)[0]

        total_entries = collection.count_documents({})
        middle_position = total_entries // 2 if total_entries % 2 == 0 else (total_entries // 2) + 1
        middle_entry = collection.find().sort('_id', 1).skip(middle_position - 1).limit(1)[0]

        last_entry = collection.find().sort('_id', -1).limit(1)[0]

        test_cases = [first_entry, middle_entry, last_entry]

        df = pd.DataFrame(test_cases)
        if '_id' in df.columns:
            df.drop('_id', axis=1, inplace=True)
        df.to_csv(output_file, index=False)
        print(f"Exported first, middle, and last test cases to '{output_file}'")
    except Exception as e:
        print(f"An error occurred: {e}")

#------------------------------------------------------------------------------------------------------------------------------------
def export_kevin_chaja_to_csv(output_file):
    collection = db['collection_2']
    try:
        
        kevin_records = collection.find({'Test Owner': 'Kevin Chaja'})
        
        df = pd.DataFrame(list(kevin_records))
        
        if '_id' in df.columns:
            df.drop('_id', axis=1, inplace=True)
        
        df.to_csv(output_file, index=False)
        print(f"Data for Kevin Chaja has been exported to {output_file}")
    except Exception as e:
        print(f"An error occurred while exporting Kevin Chaja's data to CSV: {e}")

#------------------------------------------------------------------------------------------------------------------------------------
#argparse
parser = argparse.ArgumentParser(description='Project 2')
parser.add_argument('--import_weekly', help='Path to weekly QA report CSV file to import to Collection 1', type=str)
parser.add_argument('--import_db_dump', help='Path to DB dump CSV file to import to Collection 2', type=str)
parser.add_argument('--list_user_work', help='List all work done by a specific user from both collections', type=str)
parser.add_argument('--list_repeatable', help='List all repeatable bugs from both collections', action='store_true')
parser.add_argument('--list_blockers', help='List all blocker bugs from both collections', action='store_true')
parser.add_argument('--list_build_reports', help='List all reports on a specific build from both collections', type=str)
parser.add_argument('--test_cases', action='store_true', help='Export test cases #1, #3, and the final test case to a CSV file')
parser.add_argument('--kevin_chaja', action='store_true', help='Export data for Kevin Chaja to a CSV file from Collection 2')
parser.add_argument('--output_file', help='Filename to export the CSV to', type=str)
args = parser.parse_args()


if args.import_weekly:
    parse_csv_to_collection_1(args.import_weekly)

if args.import_db_dump:
    parse_csv_to_collection_2(args.import_db_dump)

if args.list_user_work and args.output_file:
    list_work_by_user_to_csv(args.list_user_work, args.output_file)

if args.list_repeatable and args.output_file:
    export_repeatable_bugs_to_csv(args.output_file)

if args.list_blockers and args.output_file:
    export_blocker_bugs_to_csv(args.output_file)

if args.list_build_reports and args.output_file:
    export_reports_by_build_to_csv(args.list_build_reports, args.output_file)

if args.test_cases and args.output_file:
    report_test_cases(args.output_file)

if args.kevin_chaja and args.output_file:
    export_kevin_chaja_to_csv(args.output_file)