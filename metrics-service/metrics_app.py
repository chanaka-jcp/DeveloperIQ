import requests
from datetime import datetime

database_service_name = "database-service"
database_service_port = 8001  # Port at which result-service is exposed

# Construct the URL using the service name and port
database_service_url = f"http://{database_service_name}.default.svc.cluster.local:{database_service_port}/insert_metrics"
#database_service_url = "http://localhost:8001/insert_metrics"

def get_repo_metrics(repo_owner, repo_name,database_service_url):
    commits_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/commits'
    issues_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/issues'

    commits_response = requests.get(commits_url)
    issues_response = requests.get(issues_url)

    commits_info = parse_commit_data(commits_response.json(), repo_owner, repo_name)
    issues_info = parse_issue_data(issues_response.json(), repo_owner, repo_name)

    # Send data to Database Service
    database_response = requests.post(database_service_url, json={"commits": commits_info, "issues": issues_info})

    # Return the metrics
    return database_response.json()

def parse_commit_data(commits_data, repo_owner, repo_name):
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

def parse_issue_data(issues_data, repo_owner, repo_name):
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
repo_owner = 'amanchadha'
repo_name = 'coursera-deep-learning-specialization'

repo_metrics_info = get_repo_metrics(repo_owner, repo_name,database_service_url)