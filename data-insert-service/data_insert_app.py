from flask import Flask, request
from datetime import datetime
import pymssql

app = Flask(__name__)

@app.route('/data_insert', methods=['POST'])
def insert_metrics():
    data = request.get_json()
    commits = data.get('commits', [])
    issues = data.get('issues', [])
    pull_requests = data.get('pull_requests', [])

    # Azure SQL Server information
    server = 'dwcw.database.windows.net'
    database = 'DW'
    username = 'ETL_USER'
    password = 'DWH@123CW'

    # Insert commits data into Azure SQL Server
    insert_commit_data(commits, server, database, username, password)

    # Insert issues data into Azure SQL Server
    insert_issues_data(issues, server, database, username, password)

    # Insert pull requests data into Azure SQL Server
    insert_pull_requests_data(pull_requests, server, database, username, password)

    return ("Data inserted successfully")

def insert_commit_data(commits_info, server, database, username, password):
    connection = pymssql.connect(server=server, user=username, password=password, database=database)
    cursor = connection.cursor()

    # Insert data into the table
    truncate_query = "TRUNCATE TABLE User_Commits"
    cursor.execute(truncate_query)
    connection.commit()

    insert_data_query = """
    INSERT INTO User_Commits (RepoOwner, RepoName, User_name, CommitTime)
    VALUES (%s, %s, %s, %s)
    """

    for commit_info in commits_info:
        repo_owner = commit_info['repo_owner']
        repo_name = commit_info['repo_name']
        user = commit_info['user']
        commit_time = datetime.strptime(commit_info['commit_time'], "%Y-%m-%dT%H:%M:%SZ")

        cursor.execute(insert_data_query, (repo_owner, repo_name, user, commit_time))
        connection.commit()

    # Close the connection
    connection.close()

def insert_issues_data(issues_info, server, database, username, password):
    connection = pymssql.connect(server=server, user=username, password=password, database=database)
    cursor = connection.cursor()

    truncate_query = "TRUNCATE TABLE User_Issues"
    cursor.execute(truncate_query)
    connection.commit()

    # Insert data into the table
    insert_data_query = """
    INSERT INTO User_Issues (RepoOwner, RepoName, User_name, IssueTime, UpdateTime)
    VALUES (%s, %s, %s, %s, %s)
    """

    for issue_info in issues_info:
        repo_owner = issue_info['repo_owner']
        repo_name = issue_info['repo_name']
        user = issue_info['user']
        issue_time = datetime.strptime(issue_info['issue_time'], "%Y-%m-%dT%H:%M:%SZ")
        update_time = datetime.strptime(issue_info['update_time'], "%Y-%m-%dT%H:%M:%SZ")

        cursor.execute(insert_data_query, (repo_owner, repo_name, user, issue_time, update_time))
        connection.commit()

    # Close the connection
    connection.close()

def insert_pull_requests_data(pull_requests_info, server, database, username, password):
    connection = pymssql.connect(server=server, user=username, password=password, database=database)
    cursor = connection.cursor()

    truncate_query = "TRUNCATE TABLE User_Pulls"
    cursor.execute(truncate_query)
    connection.commit()

    # Insert data into the table
    insert_data_query = """
    INSERT INTO User_Pulls (RepoOwner, RepoName, User_name, PullTime, UpdateTime)
    VALUES (%s, %s, %s, %s, %s)
    """

    for pull_request_info in pull_requests_info:
        repo_owner = pull_request_info['repo_owner']
        repo_name = pull_request_info['repo_name']
        user = pull_request_info['user']
        pull_request_time = datetime.strptime(pull_request_info['pull_request_time'], "%Y-%m-%dT%H:%M:%SZ")
        update_time = datetime.strptime(pull_request_info['update_time'], "%Y-%m-%dT%H:%M:%SZ")

        cursor.execute(insert_data_query, (repo_owner, repo_name, user, pull_request_time, update_time))
        connection.commit()

    # Close the connection
    connection.close()

if __name__ == '__main__':
    app.run(debug=True, port=801, host='0.0.0.0')
