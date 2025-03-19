"""
Google Cloud Authentication Example
----------------------------------
This script demonstrates how to authenticate with Google Cloud services
using different authentication methods.
"""

import os
import json
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.auth import default
from google.cloud import storage
from dotenv import load_dotenv

# Load environment variables from .env file (if exists)
load_dotenv()

class GoogleCloudAuth:
    def __init__(self):
        """Initialize Google Cloud authentication handler."""
        self.credentials = None
        self.project_id = None
    
    def authenticate_with_adc(self):
        """
        Authenticate using Application Default Credentials (ADC).
        
        This method tries to use credentials from the environment in the following order:
        1. GOOGLE_APPLICATION_CREDENTIALS environment variable
        2. User credentials from gcloud auth application-default login
        3. GCE/GKE service account credentials
        
        Returns:
            tuple: (credentials, project_id)
        """
        try:
            credentials, project_id = default()
            self.credentials = credentials
            self.project_id = project_id
            
            # Refresh credentials if needed
            if hasattr(credentials, 'refresh') and callable(credentials.refresh):
                credentials.refresh(Request())
                
            return credentials, project_id
        except Exception as e:
            print(f"Error authenticating with ADC: {e}")
            return None, None
    
    def authenticate_with_service_account(self, service_account_file=None):
        """
        Authenticate using a service account key file.
        
        Args:
            service_account_file (str): Path to service account JSON key file
            
        Returns:
            tuple: (credentials, project_id)
        """
        # Use provided file path or try to get from environment variable
        service_account_file = service_account_file or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        
        if not service_account_file or not os.path.exists(service_account_file):
            print(f"Service account file not found: {service_account_file}")
            return None, None
        
        try:
            credentials = service_account.Credentials.from_service_account_file(
                service_account_file,
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            
            # Get project ID from the service account file
            with open(service_account_file, 'r') as f:
                service_account_info = json.load(f)
                project_id = service_account_info.get('project_id')
            
            self.credentials = credentials
            self.project_id = project_id
            
            return credentials, project_id
        except Exception as e:
            print(f"Error authenticating with service account: {e}")
            return None, None
    
    def test_authentication(self):
        """
        Test authentication by listing storage buckets.
        
        Returns:
            bool: True if authentication is successful, False otherwise
        """
        if not self.credentials:
            print("No credentials available. Please authenticate first.")
            return False
        
        try:
            # Create a client using the credentials
            storage_client = storage.Client(
                credentials=self.credentials,
                project=self.project_id
            )
            
            # List buckets to test authentication
            buckets = list(storage_client.list_buckets(max_results=1))
            print(f"Authentication successful. Project: {self.project_id}")
            return True
        except Exception as e:
            print(f"Authentication test failed: {e}")
            return False


def setup_credentials():
    """
    Interactive function to set up Google Cloud credentials.
    
    Returns:
        GoogleCloudAuth: Authenticated client
    """
    auth = GoogleCloudAuth()
    
    print("Google Cloud Authentication Setup")
    print("--------------------------------")
    print("\nChoose authentication method:")
    print("1. Application Default Credentials (ADC)")
    print("2. Service Account Key File")
    
    choice = input("\nEnter your choice (1 or 2): ")
    
    if choice == "1":
        print("\nUsing Application Default Credentials (ADC)")
        print("This method uses credentials from:")
        print("- GOOGLE_APPLICATION_CREDENTIALS environment variable")
        print("- User credentials from 'gcloud auth application-default login'")
        print("- GCE/GKE service account credentials")
        
        credentials, project_id = auth.authenticate_with_adc()
        
        if not credentials:
            print("\nADC authentication failed. Make sure you have run:")
            print("gcloud auth application-default login")
            return None
    
    elif choice == "2":
        print("\nUsing Service Account Key File")
        service_account_file = input("Enter path to service account key file: ")
        
        credentials, project_id = auth.authenticate_with_service_account(service_account_file)
        
        if not credentials:
            print("\nService account authentication failed.")
            print("Make sure the file exists and has the correct format.")
            return None
    
    else:
        print("\nInvalid choice. Trying ADC as default.")
        credentials, project_id = auth.authenticate_with_adc()
        
        if not credentials:
            print("\nAuthentication failed.")
            return None
    
    # Test authentication
    if auth.test_authentication():
        print("\nAuthentication successful!")
        return auth
    else:
        print("\nAuthentication test failed.")
        return None


def main():
    """Main function to demonstrate Google Cloud authentication."""
    print("Google Cloud Authentication Example")
    print("----------------------------------")
    
    # Try automatic authentication first
    auth = GoogleCloudAuth()
    credentials, project_id = auth.authenticate_with_adc()
    
    if credentials and auth.test_authentication():
        print(f"\nAutomatically authenticated with project: {project_id}")
    else:
        print("\nAutomatic authentication failed. Let's set up credentials.")
        auth = setup_credentials()
        
        if not auth:
            print("\nFailed to set up Google Cloud authentication.")
            print("Please make sure you have the necessary credentials.")
            return
    
    print("\nYou are now authenticated with Google Cloud!")
    print(f"Project ID: {auth.project_id}")
    print("\nYou can now use Google Cloud services in your application.")


if __name__ == "__main__":
    main()
