"""
Microsoft Graph API Email Operations Example
-------------------------------------------
This script demonstrates practical email operations using Microsoft Graph API.
It includes examples for drafting, sending, and managing emails via Outlook.
"""

import os
import json
from datetime import datetime
from configparser import ConfigParser
from azure.identity import ClientSecretCredential
from msgraph.core import GraphClient
from dotenv import load_dotenv

# Load environment variables from .env file (if exists)
load_dotenv()

class OutlookEmailManager:
    def __init__(self, client_id=None, tenant_id=None, client_secret=None):
        """
        Initialize Outlook Email Manager with Microsoft Graph API credentials.
        
        Args:
            client_id (str): Azure AD application client ID
            tenant_id (str): Azure AD tenant ID
            client_secret (str): Azure AD application client secret
        """
        # Use provided credentials or try to get from environment variables
        self.client_id = client_id or os.getenv("MS_GRAPH_CLIENT_ID")
        self.tenant_id = tenant_id or os.getenv("MS_GRAPH_TENANT_ID")
        self.client_secret = client_secret or os.getenv("MS_GRAPH_CLIENT_SECRET")
        
        if not all([self.client_id, self.tenant_id, self.client_secret]):
            raise ValueError("Missing required authentication credentials")
        
        # Initialize the credential object
        self.credential = ClientSecretCredential(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        
        # Initialize the Graph client
        self.graph_client = GraphClient(credential=self.credential)
    
    def get_inbox_messages(self, top=10, filter_string=None):
        """
        Get messages from the user's inbox with optional filtering.
        
        Args:
            top (int): Number of messages to retrieve
            filter_string (str): OData filter string
            
        Returns:
            dict: JSON response containing messages
        """
        endpoint = f"/me/mailFolders/inbox/messages?$top={top}"
        
        if filter_string:
            endpoint += f"&$filter={filter_string}"
            
        response = self.graph_client.get(endpoint)
        return response.json()
    
    def create_draft_email(self, subject, body, recipients, is_html=False, attachments=None):
        """
        Create a draft email in the user's drafts folder.
        
        Args:
            subject (str): Email subject
            body (str): Email body content
            recipients (list): List of recipient email addresses
            is_html (bool): Whether the body content is HTML
            attachments (list): List of file paths to attach
            
        Returns:
            dict: JSON response containing the created message
        """
        # Format recipients
        to_recipients = [{"emailAddress": {"address": email}} for email in recipients]
        
        # Create message payload
        message = {
            "subject": subject,
            "body": {
                "contentType": "HTML" if is_html else "Text",
                "content": body
            },
            "toRecipients": to_recipients
        }
        
        # Create the draft message
        endpoint = "/me/messages"
        response = self.graph_client.post(endpoint, json=message)
        created_message = response.json()
        
        # Add attachments if provided
        if attachments and created_message.get('id'):
            for attachment_path in attachments:
                self.add_attachment(created_message['id'], attachment_path)
        
        return created_message
    
    def add_attachment(self, message_id, file_path):
        """
        Add an attachment to an existing message.
        
        Args:
            message_id (str): ID of the message
            file_path (str): Path to the file to attach
            
        Returns:
            dict: JSON response containing the attachment info
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
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
        return response.json()
    
    def send_email(self, subject, body, recipients, is_html=False, attachments=None):
        """
        Create and send an email directly.
        
        Args:
            subject (str): Email subject
            body (str): Email body content
            recipients (list): List of recipient email addresses
            is_html (bool): Whether the body content is HTML
            attachments (list): List of file paths to attach
            
        Returns:
            dict: JSON response indicating success
        """
        # If there are attachments, create a draft first and then send it
        if attachments:
            draft = self.create_draft_email(subject, body, recipients, is_html, attachments)
            return self.send_draft(draft['id'])
        
        # Format recipients
        to_recipients = [{"emailAddress": {"address": email}} for email in recipients]
        
        # Create message payload
        message = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML" if is_html else "Text",
                    "content": body
                },
                "toRecipients": to_recipients
            }
        }
        
        endpoint = "/me/sendMail"
        response = self.graph_client.post(endpoint, json=message)
        return {"status": "sent" if response.status_code == 202 else "failed"}
    
    def send_draft(self, message_id):
        """
        Send an existing draft message.
        
        Args:
            message_id (str): ID of the draft message
            
        Returns:
            dict: JSON response indicating success
        """
        endpoint = f"/me/messages/{message_id}/send"
        response = self.graph_client.post(endpoint)
        return {"status": "sent" if response.status_code == 202 else "failed"}
    
    def schedule_email(self, subject, body, recipients, schedule_datetime, is_html=False, attachments=None):
        """
        Create a draft email and schedule it to be sent at a specific time.
        Note: This uses the draft approach as Microsoft Graph doesn't directly support scheduled sending.
        
        Args:
            subject (str): Email subject
            body (str): Email body content
            recipients (list): List of recipient email addresses
            schedule_datetime (datetime): When to send the email
            is_html (bool): Whether the body content is HTML
            attachments (list): List of file paths to attach
            
        Returns:
            dict: Information about the scheduled email
        """
        # Add scheduling information to the subject for demonstration
        scheduled_subject = f"[Scheduled for {schedule_datetime.strftime('%Y-%m-%d %H:%M')}] {subject}"
        
        # Create the draft
        draft = self.create_draft_email(scheduled_subject, body, recipients, is_html, attachments)
        
        # In a real implementation, you would use an external scheduler like Airflow
        # to trigger the sending at the specified time
        return {
            "message_id": draft['id'],
            "subject": draft['subject'],
            "scheduled_for": schedule_datetime.isoformat(),
            "status": "scheduled"
        }


def load_config(config_file='config.ini'):
    """Load configuration from a config file."""
    if not os.path.exists(config_file):
        return None
    
    config = ConfigParser()
    config.read(config_file)
    
    if 'microsoft_graph' not in config:
        return None
    
    return {
        'client_id': config['microsoft_graph'].get('client_id'),
        'tenant_id': config['microsoft_graph'].get('tenant_id'),
        'client_secret': config['microsoft_graph'].get('client_secret')
    }


def main():
    """Main function to demonstrate Outlook email operations."""
    print("Microsoft Graph API Email Operations Example")
    print("-------------------------------------------")
    
    # Try to load config from file first, then environment variables
    config = load_config()
    
    if config:
        email_manager = OutlookEmailManager(
            client_id=config['client_id'],
            tenant_id=config['tenant_id'],
            client_secret=config['client_secret']
        )
    else:
        # Use environment variables
        try:
            email_manager = OutlookEmailManager()
            print("Using credentials from environment variables")
        except ValueError as e:
            print(f"Error: {e}")
            print("\nPlease set up your credentials using microsoft_graph_config.py")
            return
    
    # Example 1: Get recent inbox messages
    try:
        print("\nGetting recent inbox messages...")
        messages = email_manager.get_inbox_messages(top=5)
        print(f"Found {len(messages.get('value', []))} messages")
        
        for idx, msg in enumerate(messages.get('value', []), 1):
            print(f"{idx}. Subject: {msg.get('subject')} - From: {msg.get('from', {}).get('emailAddress', {}).get('address')}")
    except Exception as e:
        print(f"Error getting inbox messages: {e}")
    
    # Example 2: Create a draft email with HTML content
    try:
        print("\nCreating a draft email with HTML content...")
        html_body = """
        <h2>Test HTML Email</h2>
        <p>This is a <strong>formatted</strong> email created using Microsoft Graph API.</p>
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
            <li>Item 3</li>
        </ul>
        <p>This demonstrates HTML formatting capabilities.</p>
        """
        
        draft = email_manager.create_draft_email(
            subject="HTML Test Email from Python",
            body=html_body,
            recipients=["recipient@example.com"],
            is_html=True
        )
        print(f"Draft created with ID: {draft.get('id')}")
    except Exception as e:
        print(f"Error creating draft email: {e}")
    
    # Example 3: Schedule an email (demonstration only)
    try:
        print("\nScheduling an email for future delivery...")
        scheduled_time = datetime(2025, 3, 20, 10, 0, 0)  # March 20, 2025 at 10:00 AM
        
        scheduled = email_manager.schedule_email(
            subject="Scheduled Email Test",
            body="This email was scheduled for future delivery using Python and Microsoft Graph API.",
            recipients=["recipient@example.com"],
            schedule_datetime=scheduled_time
        )
        print(f"Email scheduled: {scheduled}")
    except Exception as e:
        print(f"Error scheduling email: {e}")
    
    print("\nExamples completed.")
    print("\nNote: In a real implementation, scheduled emails would be sent using a task scheduler like Airflow.")


if __name__ == "__main__":
    main()
