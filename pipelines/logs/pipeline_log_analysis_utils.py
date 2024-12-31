import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

def check_file_not_found(log_lines, findings):
    for i, line in enumerate(log_lines, start=1):
        match = re.search(r"ls: cannot access '(.+\.ear)': No such file or directory", line)
        if match:
            findings.append((i, "FILENOTFOUND", match.group(1).strip(), "Ensure the file exists in the specified path."))


def check_permission_denied(log_lines, findings):
    for i, line in enumerate(log_lines, start=1):
        match = re.search(r".*Permission denied.*", line)
        if match:
            findings.append((i, "PERMISSION", line.strip(), "Check file permissions and ensure the script has necessary rights."))


def check_api_test_failures(log_lines, findings, url):
    for i, line in enumerate(log_lines, start=1):
        match = re.search(r"Build Automation » (.+ #(\d+)) completed: FAILURE", line)
        if match:
            job_name_with_build = match.group(1).strip()  # e.g., "FamiliesEmployeeAPITesting #585"
            job_name = job_name_with_build.split(" #")[0]  # e.g., "FamiliesEmployeeAPITesting"
            build_number = match.group(2).strip()         # e.g., "585"

            base_url = "/".join(url.split("/")[:3])  # Extract base URL, e.g., "https://jenkins.csd.ca"
            new_url = f"{base_url}/job/Automation/job/{job_name}/{build_number}/"

            findings.append((
                i,
                "APITEST",
                f"{job_name_with_build} completed: FAILURE",
                f"Investigate the test result at <a href='{new_url}'>{job_name_with_build}</a>"
            ))


def send_email(recipients, findings, url, email_body, sender_email="tcsithelp@csd.ca", smtp_server="maxdv.csd.ca"):
    msg = MIMEMultipart("alternative")
    msg["From"] = sender_email

    default_email = "bill.lin@csd.ca"
    if default_email not in recipients:
        recipients.append(default_email)

    msg["To"] = ", ".join(recipients)
    msg["Subject"] = "Jenkins Pipeline Log Analysis Results"

    msg.attach(MIMEText(email_body, "html"))

    try:
        with smtplib.SMTP(smtp_server) as server:
            server.sendmail(sender_email, recipients, msg.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")


def print_to_console(url, findings):
    print("\nJenkins Pipeline Log Analysis")
    print(f"Log URL: {url}")
    print("\nAnalyzing Results:")
    print(f"{'Line':<6} {'Category':<12} {'Description':<60} {'Advised Solution':<60}")
    print("-" * 140)
    for line_number, category, description, solution in findings:
        clean_solution = re.sub(r'<[^>]+>', '', solution)
        print(f"{line_number:<6} {category:<12} {description:<60} {clean_solution:<60}")
