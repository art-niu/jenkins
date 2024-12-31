import os
import re
import requests
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from threading import Thread
from datetime import datetime
from pipeline_log_analysis_utils import *

# Ensure proper arguments are provided
if len(sys.argv) < 4:
    print("Usage: python main.py <Jenkins URL> <Analyzer Name> <Recipient Email List>")
    exit(1)

# Parameters
url = sys.argv[1]
if url.endswith("/console"):
    url += "Text"

analyzer_name = sys.argv[2]
recipients = sys.argv[3].split(",")

# Fetch log file
username = "jenkins"
password = "YourJenkinsToken"
response = requests.get(url, auth=(username, password), verify=False)

if response.status_code != 200:
    print(f"Failed to fetch the log file. HTTP Status Code: {response.status_code}")
    exit(1)

log_lines = response.text.splitlines()
findings = []

# Execute tasks in parallel
tasks = [
    Thread(target=check_file_not_found, args=(log_lines, findings)),
    Thread(target=check_permission_denied, args=(log_lines, findings)),
    Thread(target=check_api_test_failures, args=(log_lines, findings, url))
]

for task in tasks:
    task.start()

for task in tasks:
    task.join()

# Sort findings by line number
findings.sort(key=lambda x: x[0])

# Print to console
print_to_console(url, findings)

# Generate email body
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
email_body = f"""
<html>
<head>
    <style>
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #dddddd; text-align: left; padding: 8px; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h2>Jenkins Pipeline Log Analysis</h2>
    <p><b>Jenkins Pipeline Log:</b> <a href="{url}">{url.replace('Text', '')}</a></p>
    <h3>Analyzing Results</h3>
    <table>
        <tr>
            <th>Line</th>
            <th>Category</th>
            <th>Description</th>
            <th>Advised Solution</th>
        </tr>
"""

for line_number, category, description, solution in findings:
    email_body += f"""
        <tr>
            <td>{line_number}</td>
            <td>{category}</td>
            <td>{description}</td>
            <td>{solution}</td>
        </tr>
    """

email_body += f"""
    </table>
    <p><b>Analyzed by:</b> {analyzer_name}</p>
    <p><b>Generated at:</b> {timestamp}</p>
</body>
</html>
"""

# Send email
send_email(recipients, findings, url, email_body)
