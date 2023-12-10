from flask import Flask, request, jsonify
from datetime import datetime
import pymssql

app = Flask(__name__)

@app.route('/data_insert', methods=['POST'])
def insert_metrics():
    data = request.get_json()
    commits = data.get('commits', [])
    issues = data.get('issues', [])

    # Azure SQL Server information
    server = 'dwcw.database.windows.net'
    database = 'DW'
    username = 'ETL_USER'
    password = 'DWH@123CW'

    # Insert commits data into Azure SQL Server
    insert_commit_data(commits, server, database, username, password)

    # Insert issues data into Azure SQL Server
    insert_issues_data(issues, server, database, username, password)

def insert_commit_data(commits_info, server, database, username, password):
    connection = pymssql.connect(server=server, user=username, password=password, database=database)
    cursor = connection.cursor()

    # Insert data into the table
    truncate_query="truncate table Commits" 
    cursor.execute(truncate_query)
    connection.commit()
    insert_data_query = """
    INSERT INTO Commits (RepoOwner, RepoName, User_name, CommitTime)
    VALUES (%s, %s, %s, %s)
    """
    for commit_info in commits_info:
        repo_owner = commit_info['repo_owner']
        repo_name = commit_info['repo_name']
        user = commit_info['user']
        commit_time = datetime.strptime(commit_info['commit_time'], "%Y-%m-%dT%H:%M:%SZ")  # Convert string to datetime

        cursor.execute(insert_data_query, (repo_owner, repo_name, user, commit_time))
        connection.commit()

    # Close the connection
    connection.close()

def insert_issues_data(issues_info, server, database, username, password):
    connection = pymssql.connect(server=server, user=username, password=password, database=database)
    cursor = connection.cursor()

    truncate_query="truncate table Issues" 
    cursor.execute(truncate_query)
    # Insert data into the table
    insert_data_query = """
    INSERT INTO Issues (RepoOwner, RepoName, User_name, IssueTime, UpdateTime)
    VALUES (%s, %s, %s, %s, %s)
    """
    for issue_info in issues_info:
        repo_owner = issue_info['repo_owner']
        repo_name = issue_info['repo_name']
        user = issue_info['user']
        issue_time = datetime.strptime(issue_info['issue_time'], "%Y-%m-%dT%H:%M:%SZ")  # Convert string to datetime
        update_time = datetime.strptime(issue_info['update_time'], "%Y-%m-%dT%H:%M:%SZ")  # Convert string to datetime

        cursor.execute(insert_data_query, (repo_owner, repo_name, user, issue_time, update_time))
        connection.commit()

    # Close the connection
    connection.close()

if __name__ == '__main__':
    app.run(debug=True, port=801, host='0.0.0.0')
