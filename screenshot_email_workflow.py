"""
Screenshot and Email Workflow
---------------------------
This script demonstrates how to capture screenshots from Google Managed Composer
and draft emails with those screenshots using Microsoft Graph API.
"""

import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from msgraph.core import GraphClient
from composer_browser_automation import ComposerBrowserAutomation

# Load environment variables from .env file (if exists)
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ScreenshotEmailWorkflow:
    def __init__(self):
        """Initialize the screenshot and email workflow."""
        # Microsoft Graph API credentials
        self.client_id = os.getenv("MS_GRAPH_CLIENT_ID")
        self.tenant_id = os.getenv("MS_GRAPH_TENANT_ID")
        self.client_secret = os.getenv("MS_GRAPH_CLIENT_SECRET")
        
        # Composer settings
        self.composer_url = os.getenv("COMPOSER_URL")
        self.dag_id = os.getenv("DAG_ID")
        
        # Email settings
        self.email_recipients = os.getenv("EMAIL_RECIPIENTS", "").split(",")
        
        # Initialize components
        self.graph_client = None
        self.browser_automation = None
        
        # Validate required settings
        self._validate_settings()
    
    def _validate_settings(self):
        """Validate that all required settings are available."""
        missing_vars = []
        
        if not self.client_id:
            missing_vars.append("MS_GRAPH_CLIENT_ID")
        if not self.tenant_id:
            missing_vars.append("MS_GRAPH_TENANT_ID")
        if not self.client_secret:
            missing_vars.append("MS_GRAPH_CLIENT_SECRET")
        if not self.composer_url:
            missing_vars.append("COMPOSER_URL")
        if not self.dag_id:
            missing_vars.append("DAG_ID")
        if not self.email_recipients:
            missing_vars.append("EMAIL_RECIPIENTS")
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    def initialize_graph_client(self):
        """Initialize the Microsoft Graph API client."""
        try:
            # Initialize the credential object
            credential = ClientSecretCredential(
                tenant_id=self.tenant_id,
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            
            # Initialize the Graph client
            self.graph_client = GraphClient(credential=credential)
            logger.info("Microsoft Graph API client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing Microsoft Graph API client: {e}")
            return False
    
    def initialize_browser_automation(self, headless=True):
        """Initialize the browser automation for Composer."""
        try:
            self.browser_automation = ComposerBrowserAutomation(headless=headless)
            success = self.browser_automation.setup_driver()
            if success:
                logger.info("Browser automation initialized successfully")
            return success
        except Exception as e:
            logger.error(f"Error initializing browser automation: {e}")
            return False
    
    def capture_dag_run_screenshots(self, status_filter=None, date_range=None):
        """
        Capture screenshots of DAG runs with optional filtering.
        
        Args:
            status_filter (str): Filter by run status (e.g., 'success', 'failed')
            date_range (str): Filter by date range
            
        Returns:
            tuple: (screenshot_path, run_info) or (None, None) if failed
        """
        if not self.browser_automation:
            logger.error("Browser automation not initialized")
            return None, None
        
        try:
            # Login to Composer
            if not self.browser_automation.login_to_composer(self.composer_url):
                logger.error("Failed to login to Composer")
                return None, None
            
            # Navigate to DAG runs
            if not self.browser_automation.navigate_to_dag_runs(self.dag_id):
                logger.error(f"Failed to navigate to DAG runs for {self.dag_id}")
                return None, None
            
            # Apply filters if provided
            if status_filter or date_range:
                self.browser_automation.filter_dag_runs(status=status_filter, date_range=date_range)
            
            # Take a screenshot of the filtered DAG runs
            screenshot_path = self.browser_automation.take_screenshot("dag_runs")
            
            # Get information about the last DAG run
            run_info = self.browser_automation.get_last_dag_run()
            
            return screenshot_path, run_info
        except Exception as e:
            logger.error(f"Error capturing DAG run screenshots: {e}")
            return None, None
        finally:
            # Don't close the browser here, as we might need it for more operations
            pass
    
    def draft_email_with_screenshot(self, screenshot_path, run_info, subject=None, body_template=None):
        """
        Draft an email with the DAG run screenshot using Microsoft Graph API.
        
        Args:
            screenshot_path (str): Path to the screenshot file
            run_info (dict): Information about the DAG run
            subject (str): Custom email subject
            body_template (str): Custom email body template
            
        Returns:
            dict: Created draft message or None if failed
        """
        if not self.graph_client:
            logger.error("Microsoft Graph API client not initialized")
            return None
        
        if not screenshot_path or not os.path.exists(screenshot_path):
            logger.error(f"Screenshot file not found: {screenshot_path}")
            return None
        
        try:
            # Generate email subject
            if not subject:
                dag_status = run_info.get('status', 'Unknown') if run_info else 'Unknown'
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                subject = f"DAG Run Report: {self.dag_id} - {dag_status} - {timestamp}"
            
            # Generate email body
            if not body_template:
                body_template = """
                <h2>DAG Run Report</h2>
                <p>Please find attached the screenshot of the latest DAG run for <strong>{dag_id}</strong>.</p>
                
                <h3>Run Details:</h3>
                <ul>
                    <li><strong>Run ID:</strong> {run_id}</li>
                    <li><strong>Run Type:</strong> {run_type}</li>
                    <li><strong>Execution Date:</strong> {execution_date}</li>
                    <li><strong>Start Date:</strong> {start_date}</li>
                    <li><strong>End Date:</strong> {end_date}</li>
                    <li><strong>Status:</strong> {status}</li>
                </ul>
                
                <p>This report was automatically generated at {timestamp}.</p>
                """
            
            # Format the body with run information
            body_context = {
                'dag_id': self.dag_id,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'run_id': 'N/A',
                'run_type': 'N/A',
                'execution_date': 'N/A',
                'start_date': 'N/A',
                'end_date': 'N/A',
                'status': 'N/A'
            }
            
            if run_info:
                body_context.update(run_info)
            
            body = body_template.format(**body_context)
            
            # Format recipients
            to_recipients = [{"emailAddress": {"address": email.strip()}} for email in self.email_recipients]
            
            # Create message payload
            message = {
                "subject": subject,
                "body": {
                    "contentType": "HTML",
                    "content": body
                },
                "toRecipients": to_recipients
            }
            
            # Create the draft message
            endpoint = "/me/messages"
            response = self.graph_client.post(endpoint, json=message)
            created_message = response.json()
            
            # Add the screenshot as an attachment
            self.add_attachment_to_message(created_message['id'], screenshot_path)
            
            logger.info(f"Draft email created with subject: {subject}")
            return created_message
        except Exception as e:
            logger.error(f"Error drafting email: {e}")
            return None
    
    def add_attachment_to_message(self, message_id, file_path):
        """
        Add an attachment to an existing message.
        
        Args:
            message_id (str): ID of the message
            file_path (str): Path to the file to attach
            
        Returns:
            dict: Attachment info or None if failed
        """
        if not self.graph_client:
            logger.error("Microsoft Graph API client not initialized")
            return None
        
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None
        
        try:
            # Read file content
            with open(file_path, 'rb') as file:
                content = file.read()
            
            # Get file name and encode content
            file_name = os.path.basename(file_path)
            import base64
            content_bytes = base64.b64encode(content).decode('utf-8')
            
            # Create attachment payload
            attachment = {
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": file_name,
                "contentBytes": content_bytes
            }
            
            # Add attachment to message
            endpoint = f"/me/messages/{message_id}/attachments"
            response = self.graph_client.post(endpoint, json=attachment)
            attachment_info = response.json()
            
            logger.info(f"Attachment added to message: {file_name}")
            return attachment_info
        except Exception as e:
            logger.error(f"Error adding attachment: {e}")
            return None
    
    def send_email(self, message_id):
        """
        Send a draft email.
        
        Args:
            message_id (str): ID of the draft message
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.graph_client:
            logger.error("Microsoft Graph API client not initialized")
            return False
        
        try:
            endpoint = f"/me/messages/{message_id}/send"
            response = self.graph_client.post(endpoint)
            success = response.status_code == 202
            
            if success:
                logger.info(f"Email sent successfully")
            else:
                logger.error(f"Failed to send email: {response.status_code}")
            
            return success
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources."""
        if self.browser_automation:
            self.browser_automation.close()
            logger.info("Browser automation resources cleaned up")


def main():
    """Main function to demonstrate the screenshot and email workflow."""
    # Initialize the workflow
    workflow = ScreenshotEmailWorkflow()
    
    try:
        # Initialize components
        if not workflow.initialize_graph_client():
            logger.error("Failed to initialize Microsoft Graph API client")
            return
        
        if not workflow.initialize_browser_automation(headless=False):
            logger.error("Failed to initialize browser automation")
            return
        
        # Capture DAG run screenshots with filtering
        screenshot_path, run_info = workflow.capture_dag_run_screenshots(
            status_filter="success",  # Filter for successful runs
            date_range=None  # No date range filter
        )
        
        if not screenshot_path or not run_info:
            logger.error("Failed to capture DAG run screenshots or get run information")
            return
        
        # Draft an email with the screenshot
        draft_message = workflow.draft_email_with_screenshot(screenshot_path, run_info)
        
        if not draft_message:
            logger.error("Failed to draft email")
            return
        
        print(f"\nDraft email created with subject: {draft_message['subject']}")
        print(f"Message ID: {draft_message['id']}")
        
        # Ask if the user wants to send the email
        send_email = input("\nDo you want to send the email? (y/n): ")
        if send_email.lower() == 'y':
            if workflow.send_email(draft_message['id']):
                print("Email sent successfully")
            else:
                print("Failed to send email")
        else:
            print("Email saved as draft")
    
    finally:
        # Clean up
        workflow.cleanup()


if __name__ == "__main__":
    main()
