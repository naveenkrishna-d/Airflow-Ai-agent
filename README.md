# Airflow DAG Screenshot and Email Automation

This project provides an automated solution for:
1. Logging into Google Managed Composer (Airflow)
2. Capturing screenshots of DAG runs based on filter conditions
3. Drafting and optionally sending emails with those screenshots via Outlook

## Project Structure

```
python_automation_project/
├── venv/                           # Python virtual environment
├── screenshots/                    # Directory for captured screenshots
├── main.py                         # Main entry point for the application
├── composer_browser_automation.py  # Browser automation for Composer
├── screenshot_email_workflow.py    # Screenshot and email workflow
├── microsoft_graph_example.py      # Microsoft Graph API example
├── microsoft_graph_config.py       # Microsoft Graph API configuration
├── microsoft_graph_email_operations.py # Advanced email operations
├── google_cloud_auth.py            # Google Cloud authentication
├── google_cloud_storage.py         # Google Cloud Storage operations
├── google_cloud_bigquery.py        # Google Cloud BigQuery operations
├── airflow_basic_dag.py            # Basic Airflow DAG example
├── requirements.txt                # Python dependencies
└── .env                            # Environment variables (create this file)
```

## Prerequisites

1. Python 3.8 or higher
2. Google Cloud account with Composer (Airflow) environment
3. Microsoft Azure account with registered application for Graph API
4. Chrome browser installed (for Selenium)

## Installation

1. Clone the repository or copy the files to your local machine
2. Create a virtual environment and install dependencies:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

3. Create a `.env` file with the following environment variables:

```
# Microsoft Graph API credentials
MS_GRAPH_CLIENT_ID=your_client_id
MS_GRAPH_TENANT_ID=your_tenant_id
MS_GRAPH_CLIENT_SECRET=your_client_secret

# Composer settings
COMPOSER_URL=https://your-composer-environment-url
DAG_ID=your_dag_id

# Email settings
EMAIL_RECIPIENTS=recipient1@example.com,recipient2@example.com
```

## Usage

### Basic Usage

Run the main script:

```bash
python main.py
```

This will:
1. Log into your Composer environment
2. Navigate to the specified DAG
3. Capture a screenshot of the DAG runs
4. Draft an email with the screenshot
5. Ask if you want to send the email

### Command Line Options

```
usage: main.py [-h] [--headless] [--dag-id DAG_ID]
               [--status-filter {success,failed,running}]
               [--date-range DATE_RANGE] [--email-subject EMAIL_SUBJECT]
               [--email-recipients EMAIL_RECIPIENTS] [--send-email]
               [--config CONFIG]

Composer Screenshot and Email Automation

optional arguments:
  -h, --help            show this help message and exit
  --headless            Run browser in headless mode
  --dag-id DAG_ID       ID of the DAG to capture (overrides environment variable)
  --status-filter {success,failed,running}
                        Filter DAG runs by status
  --date-range DATE_RANGE
                        Filter DAG runs by date range (e.g., "2025-03-01 to 2025-03-13")
  --email-subject EMAIL_SUBJECT
                        Custom email subject
  --email-recipients EMAIL_RECIPIENTS
                        Comma-separated list of email recipients (overrides environment variable)
  --send-email          Automatically send the email instead of saving as draft
  --config CONFIG       Path to configuration file
```

### Configuration File

You can also use a JSON configuration file:

```json
{
  "ms_graph_client_id": "your_client_id",
  "ms_graph_tenant_id": "your_tenant_id",
  "ms_graph_client_secret": "your_client_secret",
  "composer_url": "https://your-composer-environment-url",
  "dag_id": "your_dag_id",
  "email_recipients": ["recipient1@example.com", "recipient2@example.com"],
  "headless": true,
  "status_filter": "success",
  "date_range": "2025-03-01 to 2025-03-13",
  "email_subject": "Custom DAG Run Report",
  "send_email": true
}
```

Then run:

```bash
python main.py --config config.json
```

## Scheduling with Google Cloud Functions or Vertex AI

### Google Cloud Functions

1. Create a new Cloud Function
2. Set the runtime to Python 3.9+
3. Set the entry point to `run_automation`
4. Upload the code files
5. Set environment variables in the Cloud Function configuration
6. Set up a Cloud Scheduler job to trigger the function on your desired schedule

### Vertex AI

1. Package the code as a custom container
2. Create a Vertex AI custom job
3. Set up a Cloud Scheduler job to trigger the Vertex AI job on your desired schedule

## Components

### Browser Automation (`composer_browser_automation.py`)

This component handles:
- Setting up the Chrome WebDriver
- Logging into Google Managed Composer
- Navigating to DAG runs
- Applying filters
- Taking screenshots
- Extracting information about DAG runs

### Screenshot and Email Workflow (`screenshot_email_workflow.py`)

This component handles:
- Initializing Microsoft Graph API client
- Capturing DAG run screenshots
- Drafting emails with screenshots
- Adding attachments to emails
- Sending emails

### Main Application (`main.py`)

This is the main entry point that:
- Parses command line arguments
- Loads and validates configuration
- Orchestrates the entire workflow
- Handles errors and logging

## Troubleshooting

### Authentication Issues

- For Microsoft Graph API:
  - Ensure your application has the correct permissions (Mail.ReadWrite, Mail.Send)
  - Verify your client ID, tenant ID, and client secret

- For Google Composer:
  - Ensure you have access to the Composer environment
  - The browser automation assumes you're already authenticated with Google

### Browser Automation Issues

- Make sure Chrome is installed
- If running in headless mode on a server, ensure all dependencies are installed
- Adjust timeouts if pages are loading slowly

### Email Issues

- Check that your email recipients are valid
- Verify your application has the necessary permissions
- Check the automation.log file for detailed error messages

## Extending the Project

### Adding More Filters

Modify the `filter_dag_runs` method in `composer_browser_automation.py` to support additional filters.

### Customizing Email Templates

Modify the `draft_email_with_screenshot` method in `screenshot_email_workflow.py` to customize the email template.

### Supporting Other Browsers

Modify the `setup_driver` method in `composer_browser_automation.py` to support other browsers like Firefox or Edge.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
