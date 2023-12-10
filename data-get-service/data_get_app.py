from flask import Flask, render_template
import requests
from datetime import datetime
import schedule
import time

app = Flask(__name__)

# Construct the URL using the service name and port
datainsert_service_url = f"http://data-insert-service.default.svc.cluster.local:801/data_insert"
def job():
    print(f"Running job at {datetime.now()}")

    # Your existing code to get repo metrics
    repo_owner = 'amanchadha'
    repo_name = 'coursera-deep-learning-specialization'
    repo_metrics_info = post_data(repo_owner, repo_name, datainsert_service_url)


def post_data(repo_owner, repo_name, datainsert_service_url):
    commits_info = get_commit_data(repo_owner, repo_name)
    issues_info = get_issue_data( repo_owner, repo_name)

    # Send data to Database Service
    database_response = requests.post(datainsert_service_url, json={"commits": commits_info, "issues": issues_info})

    # Return the metrics
    return database_response.json()


def get_commit_data(repo_owner, repo_name):
    commits_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/commits'
    commits_response = requests.get(commits_url)
    commits_data=commits_response.json()
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
    issues_data=issues_response.json()
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


# Schedule the job to run every hour
schedule.every().hour.do(job)
# Run the scheduler in a separate thread
def scheduler_thread():
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    import threading
    threading.Thread(target=scheduler_thread, daemon=True).start()# Start the scheduler thread

    # Start the Flask app
    app.run(debug=True, port=800, host='0.0.0.0')
