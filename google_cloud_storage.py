"""
Google Cloud Storage Operations Example
--------------------------------------
This script demonstrates how to interact with Google Cloud Storage
using the Google Cloud Storage client library.
"""

import os
import io
from google.cloud import storage
from google.oauth2 import service_account
from google.auth import default
from dotenv import load_dotenv

# Load environment variables from .env file (if exists)
load_dotenv()

class GCPStorageManager:
    def __init__(self, credentials=None, project_id=None):
        """
        Initialize Google Cloud Storage manager.
        
        Args:
            credentials: Google Cloud credentials
            project_id (str): Google Cloud project ID
        """
        if credentials:
            self.credentials = credentials
            self.project_id = project_id
        else:
            # Try to get credentials from ADC
            try:
                self.credentials, self.project_id = default()
            except Exception as e:
                print(f"Error getting default credentials: {e}")
                self.credentials = None
                self.project_id = None
        
        if self.credentials:
            self.client = storage.Client(
                credentials=self.credentials,
                project=self.project_id
            )
        else:
            raise ValueError("No valid credentials provided")
    
    def list_buckets(self, max_results=None):
        """
        List storage buckets in the project.
        
        Args:
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of bucket names
        """
        try:
            buckets = list(self.client.list_buckets(max_results=max_results))
            return [bucket.name for bucket in buckets]
        except Exception as e:
            print(f"Error listing buckets: {e}")
            return []
    
    def create_bucket(self, bucket_name, location="us-central1"):
        """
        Create a new storage bucket.
        
        Args:
            bucket_name (str): Name of the bucket to create
            location (str): Location for the bucket
            
        Returns:
            storage.Bucket: Created bucket or None if failed
        """
        try:
            bucket = self.client.bucket(bucket_name)
            bucket.create(location=location)
            print(f"Bucket {bucket_name} created in {location}")
            return bucket
        except Exception as e:
            print(f"Error creating bucket {bucket_name}: {e}")
            return None
    
    def upload_file(self, bucket_name, source_file_path, destination_blob_name=None):
        """
        Upload a file to a bucket.
        
        Args:
            bucket_name (str): Name of the bucket
            source_file_path (str): Path to the source file
            destination_blob_name (str): Name of the destination blob
            
        Returns:
            storage.Blob: Uploaded blob or None if failed
        """
        if not os.path.exists(source_file_path):
            print(f"Source file not found: {source_file_path}")
            return None
        
        # If destination blob name is not provided, use the source file name
        if not destination_blob_name:
            destination_blob_name = os.path.basename(source_file_path)
        
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(destination_blob_name)
            
            # Upload the file
            blob.upload_from_filename(source_file_path)
            print(f"File {source_file_path} uploaded to {bucket_name}/{destination_blob_name}")
            
            return blob
        except Exception as e:
            print(f"Error uploading file: {e}")
            return None
    
    def download_file(self, bucket_name, source_blob_name, destination_file_path):
        """
        Download a blob from a bucket.
        
        Args:
            bucket_name (str): Name of the bucket
            source_blob_name (str): Name of the source blob
            destination_file_path (str): Path to the destination file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(source_blob_name)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(destination_file_path)), exist_ok=True)
            
            # Download the blob
            blob.download_to_filename(destination_file_path)
            print(f"Blob {bucket_name}/{source_blob_name} downloaded to {destination_file_path}")
            
            return True
        except Exception as e:
            print(f"Error downloading file: {e}")
            return False
    
    def list_blobs(self, bucket_name, prefix=None):
        """
        List blobs in a bucket.
        
        Args:
            bucket_name (str): Name of the bucket
            prefix (str): Filter results to objects whose names begin with this prefix
            
        Returns:
            list: List of blob names
        """
        try:
            bucket = self.client.bucket(bucket_name)
            blobs = list(bucket.list_blobs(prefix=prefix))
            return [blob.name for blob in blobs]
        except Exception as e:
            print(f"Error listing blobs: {e}")
            return []
    
    def delete_blob(self, bucket_name, blob_name):
        """
        Delete a blob from a bucket.
        
        Args:
            bucket_name (str): Name of the bucket
            blob_name (str): Name of the blob to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.delete()
            print(f"Blob {bucket_name}/{blob_name} deleted")
            return True
        except Exception as e:
            print(f"Error deleting blob: {e}")
            return False
    
    def generate_signed_url(self, bucket_name, blob_name, expiration=3600):
        """
        Generate a signed URL for a blob.
        
        Args:
            bucket_name (str): Name of the bucket
            blob_name (str): Name of the blob
            expiration (int): URL expiration time in seconds
            
        Returns:
            str: Signed URL or None if failed
        """
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            url = blob.generate_signed_url(
                version="v4",
                expiration=expiration,
                method="GET"
            )
            
            print(f"Generated signed URL for {bucket_name}/{blob_name}")
            return url
        except Exception as e:
            print(f"Error generating signed URL: {e}")
            return None


def create_test_file(file_path, content="This is a test file for GCP Storage demo"):
    """Create a test file with the given content."""
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error creating test file: {e}")
        return False


def main():
    """Main function to demonstrate Google Cloud Storage operations."""
    print("Google Cloud Storage Operations Example")
    print("--------------------------------------")
    
    # Try to authenticate
    try:
        storage_manager = GCPStorageManager()
        print(f"Authenticated with project: {storage_manager.project_id}")
    except ValueError as e:
        print(f"Authentication error: {e}")
        print("\nPlease set up Google Cloud authentication first.")
        print("You can run google_cloud_auth.py to set up authentication.")
        return
    
    # List buckets
    print("\nListing buckets:")
    buckets = storage_manager.list_buckets()
    if buckets:
        for i, bucket in enumerate(buckets, 1):
            print(f"{i}. {bucket}")
    else:
        print("No buckets found or error listing buckets.")
    
    # Create a test file
    test_file_path = "test_upload.txt"
    if create_test_file(test_file_path):
        print(f"\nCreated test file: {test_file_path}")
    
    # Interactive bucket selection or creation
    print("\nChoose an operation:")
    print("1. Use an existing bucket")
    print("2. Create a new bucket")
    
    choice = input("\nEnter your choice (1 or 2): ")
    
    if choice == "1":
        if not buckets:
            print("No buckets available. Please create a bucket first.")
            return
        
        print("\nSelect a bucket:")
        for i, bucket in enumerate(buckets, 1):
            print(f"{i}. {bucket}")
        
        bucket_idx = int(input("\nEnter bucket number: ")) - 1
        if 0 <= bucket_idx < len(buckets):
            bucket_name = buckets[bucket_idx]
        else:
            print("Invalid bucket selection.")
            return
    
    elif choice == "2":
        bucket_name = input("\nEnter new bucket name: ")
        location = input("Enter bucket location (default: us-central1): ") or "us-central1"
        
        bucket = storage_manager.create_bucket(bucket_name, location)
        if not bucket:
            print("Failed to create bucket. Exiting.")
            return
    
    else:
        print("Invalid choice. Exiting.")
        return
    
    # Upload the test file
    print(f"\nUploading file to bucket {bucket_name}...")
    blob = storage_manager.upload_file(bucket_name, test_file_path)
    
    if blob:
        # List blobs in the bucket
        print(f"\nListing blobs in bucket {bucket_name}:")
        blobs = storage_manager.list_blobs(bucket_name)
        for i, blob_name in enumerate(blobs, 1):
            print(f"{i}. {blob_name}")
        
        # Generate a signed URL for the uploaded file
        if test_file_path in blobs or os.path.basename(test_file_path) in blobs:
            blob_name = test_file_path if test_file_path in blobs else os.path.basename(test_file_path)
            url = storage_manager.generate_signed_url(bucket_name, blob_name)
            if url:
                print(f"\nSigned URL for {blob_name}: {url}")
                print("This URL will expire in 1 hour.")
    
    # Clean up
    print("\nDo you want to delete the test file from the bucket? (y/n)")
    if input().lower() == 'y':
        blob_name = os.path.basename(test_file_path)
        if storage_manager.delete_blob(bucket_name, blob_name):
            print("Test file deleted from bucket.")
    
    # Remove local test file
    try:
        os.remove(test_file_path)
        print(f"Local test file {test_file_path} removed.")
    except Exception as e:
        print(f"Error removing local test file: {e}")
    
    print("\nExample completed.")


if __name__ == "__main__":
    main()
