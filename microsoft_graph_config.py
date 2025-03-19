"""
Microsoft Graph API Configuration Example
----------------------------------------
This script demonstrates how to set up a configuration file for Microsoft Graph API
and test the connection with the provided credentials.
"""

import os
import json
from configparser import ConfigParser
from dotenv import load_dotenv

# Load environment variables from .env file (if exists)
load_dotenv()

def create_config_file(config_file='config.ini'):
    """Create a configuration file with Microsoft Graph API settings."""
    config = ConfigParser()
    
    # Check if file exists and has the microsoft_graph section
    if os.path.exists(config_file):
        config.read(config_file)
    
    if 'microsoft_graph' not in config:
        config['microsoft_graph'] = {}
    
    # Get credentials from environment variables or prompt user
    client_id = os.getenv("MS_GRAPH_CLIENT_ID")
    tenant_id = os.getenv("MS_GRAPH_TENANT_ID")
    client_secret = os.getenv("MS_GRAPH_CLIENT_SECRET")
    
    if not client_id:
        client_id = input("Enter your Azure AD application client ID: ")
    if not tenant_id:
        tenant_id = input("Enter your Azure AD tenant ID: ")
    if not client_secret:
        client_secret = input("Enter your Azure AD application client secret: ")
    
    # Update config
    config['microsoft_graph']['client_id'] = client_id
    config['microsoft_graph']['tenant_id'] = tenant_id
    config['microsoft_graph']['client_secret'] = client_secret
    
    # Write to file
    with open(config_file, 'w') as f:
        config.write(f)
    
    print(f"Configuration saved to {config_file}")
    return config

def create_env_file(env_file='.env'):
    """Create a .env file with Microsoft Graph API environment variables."""
    # Check if file exists
    env_vars = {}
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
    
    # Get credentials from user input if not in environment
    client_id = os.getenv("MS_GRAPH_CLIENT_ID")
    tenant_id = os.getenv("MS_GRAPH_TENANT_ID")
    client_secret = os.getenv("MS_GRAPH_CLIENT_SECRET")
    
    if not client_id:
        client_id = input("Enter your Azure AD application client ID: ")
    if not tenant_id:
        tenant_id = input("Enter your Azure AD tenant ID: ")
    if not client_secret:
        client_secret = input("Enter your Azure AD application client secret: ")
    
    # Update env vars
    env_vars["MS_GRAPH_CLIENT_ID"] = client_id
    env_vars["MS_GRAPH_TENANT_ID"] = tenant_id
    env_vars["MS_GRAPH_CLIENT_SECRET"] = client_secret
    
    # Write to file
    with open(env_file, 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    
    print(f"Environment variables saved to {env_file}")

def main():
    """Main function to set up Microsoft Graph API configuration."""
    print("Microsoft Graph API Configuration Setup")
    print("--------------------------------------")
    
    print("\nThis script will help you set up the configuration for Microsoft Graph API.")
    print("You will need the following information:")
    print("1. Azure AD application client ID")
    print("2. Azure AD tenant ID")
    print("3. Azure AD application client secret")
    
    config_type = input("\nChoose configuration type (1 for config.ini, 2 for .env): ")
    
    if config_type == "1":
        create_config_file()
    elif config_type == "2":
        create_env_file()
    else:
        print("Invalid choice. Creating both config files.")
        create_config_file()
        create_env_file()
    
    print("\nConfiguration setup complete.")
    print("\nTo use Microsoft Graph API, your Azure AD application needs the following permissions:")
    print("- Mail.ReadWrite")
    print("- Mail.Send")
    print("- User.Read")
    
    print("\nYou can now run the microsoft_graph_example.py script to test the integration.")

if __name__ == "__main__":
    main()
