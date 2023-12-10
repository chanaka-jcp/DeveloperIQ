from flask import Flask, render_template
import requests
from datetime import datetime
import schedule
import time

app = Flask(__name__)

# Construct the URL using the service name and port
datainsert_service_url = "http://data-insert-service.default.svc.cluster.local:801/data_insert"
#datainsert_service_url = "http://localhost:801/data_insert"
def job():
    print(f"Running job at {datetime.now()}")

    repo_owner = 'Azure'
    repo_name = 'FTALive-Sessions'

    commits_info = get_commit_data(repo_owner, repo_name)
    issues_info = get_issue_data(repo_owner, repo_name)
    pull_requests_info = get_pull_request_data(repo_owner, repo_name)

    # Send data to Database Service
    database_response = requests.post(datainsert_service_url, json={
        "commits": commits_info,
        "issues": issues_info,
        "pull_requests": pull_requests_info
    })

    if database_response.text:
        return database_response.json()
    else:
        print("Empty response received.")
def get_commit_data(repo_owner, repo_name):
    commits_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/commits'
    commits_response = requests.get(commits_url)
    commits_data = commits_response.json()
    commits_info = []
    for commit in commits_data:
        user_login = commit['author']['login'] if commit['author'] is not None and 'login' in commit['author'] else None
        commit_data = {
            'repo_owner': repo_owner,
            'repo_name': repo_name,
            'user': user_login,
            'commit_time': commit['commit']['author']['date']
        }
        commits_info.append(commit_data)
    return commits_info

def get_issue_data(repo_owner, repo_name):
    issues_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/issues'
    issues_response = requests.get(issues_url)
    issues_data = issues_response.json()
    issues_info = []
    for issue in issues_data:
        issue_data = {
            'repo_owner': repo_owner,
            'repo_name': repo_name,
            'user': issue['user']['login'],
            'issue_time': issue['created_at'],
            'update_time': issue['updated_at']
        }
        issues_info.append(issue_data)
    return issues_info

def get_pull_request_data(repo_owner, repo_name):
    pull_requests_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/pulls'
    pull_requests_response = requests.get(pull_requests_url)
    pull_requests_data = pull_requests_response.json()
    pull_requests_info = []
    for pull_request in pull_requests_data:
        user_login = pull_request['user']['login'] if 'user' in pull_request and 'login' in pull_request['user'] else None
        pull_request_data = {
            'repo_owner': repo_owner,
            'repo_name': repo_name,
            'user': user_login,
            'pull_request_time': pull_request['created_at'],
            'update_time': pull_request['updated_at']
        }
        pull_requests_info.append(pull_request_data)
    return pull_requests_info

# Schedule the job to run every hour
#schedule.every().hour.do(job)
schedule.every(5).minutes.do(job)
# Run the scheduler in a separate thread
def scheduler_thread():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    import threading
    threading.Thread(target=scheduler_thread, daemon=True).start() # Start the scheduler thread

    # Start the Flask app
    app.run(debug=True, port=800, host='0.0.0.0')
