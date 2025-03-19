"""
Microsoft Graph API Integration Example
--------------------------------------
This script demonstrates how to authenticate with Microsoft Graph API
and perform email operations (drafting and sending emails via Outlook).

Requirements:
- Azure AD app registration with appropriate permissions
- Client ID, Tenant ID, and Client Secret
"""

import os
import json
from configparser import ConfigParser
from azure.identity import ClientSecretCredential
from msgraph.core import GraphClient
from dotenv import load_dotenv

# Load environment variables from .env file (if exists)
load_dotenv()

class MicrosoftGraphAPI:
    def __init__(self, client_id=None, tenant_id=None, client_secret=None):
        """
        Initialize Microsoft Graph API client with authentication credentials.
        
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
    
    def get_me(self):
        """Get information about the authenticated user."""
        endpoint = "/me"
        response = self.graph_client.get(endpoint)
        return response.json()
    
    def list_messages(self, top=10):
        """
        List recent emails in the user's inbox.
        
        Args:
            top (int): Number of messages to retrieve
            
        Returns:
            dict: JSON response containing messages
        """
        endpoint = f"/me/messages?$top={top}"
        response = self.graph_client.get(endpoint)
        return response.json()
    
    def create_draft_email(self, subject, body, recipients):
        """
        Create a draft email in the user's drafts folder.
        
        Args:
            subject (str): Email subject
            body (str): Email body content
            recipients (list): List of recipient email addresses
            
        Returns:
            dict: JSON response containing the created message
        """
        # Format recipients
        to_recipients = [{"emailAddress": {"address": email}} for email in recipients]
        
        # Create message payload
        message = {
            "subject": subject,
            "body": {
                "contentType": "Text",
                "content": body
            },
            "toRecipients": to_recipients
        }
        
        endpoint = "/me/messages"
        response = self.graph_client.post(endpoint, json=message)
        return response.json()
    
    def send_email(self, subject, body, recipients):
        """
        Create and send an email directly.
        
        Args:
            subject (str): Email subject
            body (str): Email body content
            recipients (list): List of recipient email addresses
            
        Returns:
            dict: JSON response indicating success
        """
        # Format recipients
        to_recipients = [{"emailAddress": {"address": email}} for email in recipients]
        
        # Create message payload
        message = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "Text",
                    "content": body
                },
                "toRecipients": to_recipients
            }
        }
        
        endpoint = "/me/sendMail"
        response = self.graph_client.post(endpoint, json=message)
        return {"status": "sent" if response.status_code == 202 else "failed"}


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
    """Main function to demonstrate Microsoft Graph API integration."""
    print("Microsoft Graph API Integration Example")
    print("---------------------------------------")
    
    # Try to load config from file first, then environment variables
    config = load_config()
    
    if config:
        graph_api = MicrosoftGraphAPI(
            client_id=config['client_id'],
            tenant_id=config['tenant_id'],
            client_secret=config['client_secret']
        )
    else:
        # Use environment variables
        try:
            graph_api = MicrosoftGraphAPI()
            print("Using credentials from environment variables")
        except ValueError as e:
            print(f"Error: {e}")
            print("\nPlease set the following environment variables:")
            print("  MS_GRAPH_CLIENT_ID: Your Azure AD application client ID")
            print("  MS_GRAPH_TENANT_ID: Your Azure AD tenant ID")
            print("  MS_GRAPH_CLIENT_SECRET: Your Azure AD application client secret")
            print("\nOr create a config.ini file with the following content:")
            print("[microsoft_graph]")
            print("client_id = your_client_id")
            print("tenant_id = your_tenant_id")
            print("client_secret = your_client_secret")
            return
    
    # Example 1: Get user information
    try:
        print("\nGetting user information...")
        user_info = graph_api.get_me()
        print(f"Logged in as: {user_info.get('displayName')} ({user_info.get('userPrincipalName')})")
    except Exception as e:
        print(f"Error getting user information: {e}")
    
    # Example 2: Create a draft email
    try:
        print("\nCreating a draft email...")
        draft = graph_api.create_draft_email(
            subject="Test Draft Email from Python",
            body="This is a test draft email created using Microsoft Graph API and Python.",
            recipients=["recipient@example.com"]
        )
        print(f"Draft created with ID: {draft.get('id')}")
    except Exception as e:
        print(f"Error creating draft email: {e}")
    
    # Example 3: Send an email (commented out to prevent actual sending)
    """
    try:
        print("\nSending an email...")
        result = graph_api.send_email(
            subject="Test Email from Python",
            body="This is a test email sent using Microsoft Graph API and Python.",
            recipients=["recipient@example.com"]
        )
        print(f"Email sending status: {result.get('status')}")
    except Exception as e:
        print(f"Error sending email: {e}")
    """
    
    print("\nExamples completed.")


if __name__ == "__main__":
    main()
