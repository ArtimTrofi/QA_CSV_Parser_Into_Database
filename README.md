# QA CSV Parser Into Database

## Artim Trofimenko

### Overview

The QA CSV Parser is a dedicated tool designed to automate the collection and input of QA CSV data into a MongoDB database. This tool supports features like parsing weekly QA reports, importing mock DB dumps, and generating various reports from the database.
This project aims to simplify the process of managing and querying QA reports using Python and MongoDB. By using Argparse, it offers a user-friendly command-line interface for performing various database operations programmatically.

### Features

- **Import Weekly QA Reports**: Import your weekly QA reports into Collection 1 of the database.
- **Mock DB Dump Import**: Input a mock "DB dump" which contains everyone's reports into Collection 2.
- **User Work Export**: List all work done by a specific user from both collections (no duplicates).
- **Repeatable Bugs Export**: Export all repeatable bugs from both collections (no duplicates).
- **Blocker Bugs Export**: Export all blocker bugs from both collections (no duplicates).
- **Build Reports Export**: Export all reports on a specific build date from both collections (no duplicates).
- **Test Cases Report**: Report the first, middle, and last test cases from collection 2.
- **User Data Export**: Export data for a specific user using Argparse.

### Current Repository Files

- **.gitignore**: Configured to exclude the `SUBMISSION` folder and other unnecessary files.
- **script.py**: The main script for parsing and exporting QA data.
- **artim_work.csv**: All work done by your user.
- **blockers.csv**: All blocker bugs from both collections.
- **Builds_3_19.csv**: All reports on build 3/19/2024 from both collections.
- **TestCases.csv**: First, middle, and last test cases from collection 2.
- **Chaja.csv**: Export of user Kevin Chaja.

### Setup

1. **Install Dependencies**:  
   Ensure you have Python and MongoDB installed. Install the required Python packages using: pip install pandas pymongo

2. **Configure MongoDB**:  
   Ensure MongoDB is running on your local machine or update the connection string in the script to point to your MongoDB instance.

3. **Run the script**:
                      
   **Import weekly QA report**: python script.py --import_weekly path/to/weekly_report.xlsx
   
   **Import DB dump**: python script.py --import_db_dump path/to/db_dump.xlsx

   **List all work done by a user**: python script.py --list_user_work "User Name" --output_file output.csv
   
   **Export repeatable bugs**: python script.py --list_repeatable --output_file repeatable_bugs.csv

   **Export blocker bugs**: python script.py --list_blockers --output_file blocker_bugs.csv

   **Export reports by build date**: python script.py --list_build_reports "03/19/2024" --output_file build_reports.csv

   **Export specific test cases**: python script.py --test_cases --output_file test_cases.csv

   **Export data for Kevin Chaja**: python script.py --kevin_chaja --output_file kevin_chaja.csv
