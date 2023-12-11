from flask import Flask, render_template
import pymssql

app = Flask(__name__)

# Azure SQL Server information
server = 'dwcw.database.windows.net'
database = 'DW'
username = 'ETL_USER'
password = 'DWH@123CW'

def execute_query(query):
    connection = pymssql.connect(server=server, user=username, password=password, database=database)
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    connection.close()
    return result

@app.route('/')
def index():
    # Query to get user commits count
    commits_query = "SELECT User_name, COUNT(*) AS n_commits FROM User_Commits WHERE User_name IS NOT NULL GROUP BY User_name"
    commits_result = execute_query(commits_query)

    # Query to get user issues count
    pulls_query = "SELECT User_name, COUNT(*) AS n_pulls FROM User_Pulls WHERE User_name IS NOT NULL GROUP BY User_name"
    pulls_result = execute_query(pulls_query)

    # Query to get average time to complete issues in hours
    avg_time_query = """
    SELECT user_name, SUM(DATEDIFF(MINUTE, IssueTime, UpdateTime))/COUNT(*) AS avgTimeToCompleteInHours
    FROM User_Issues
    WHERE User_name IS NOT NULL
    GROUP BY user_name
    """
    avg_time_result = execute_query(avg_time_query)

    return render_template('result.html', commits_result=commits_result, pulls_result=pulls_result, avg_time_result=avg_time_result)

if __name__ == '__main__':
    app.run(debug=True, port=802, host='0.0.0.0')