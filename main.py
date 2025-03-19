"""
Combined End-to-End Solution
--------------------------
This script provides a complete end-to-end solution for automating the process of:
1. Logging into Google Managed Composer (Airflow)
2. Capturing screenshots of DAG runs based on filter conditions
3. Drafting and optionally sending emails with those screenshots via Outlook

This can be run as a standalone script or scheduled as a job using Vertex AI or Google Cloud Functions.
"""

import os
import sys
import argparse
import logging
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("automation.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Composer Screenshot and Email Automation')
    
    parser.add_argument('--headless', action='store_true', 
                        help='Run browser in headless mode')
    
    parser.add_argument('--dag-id', type=str,
                        help='ID of the DAG to capture (overrides environment variable)')
    
    parser.add_argument('--status-filter', type=str, choices=['success', 'failed', 'running'],
                        help='Filter DAG runs by status')
    
    parser.add_argument('--date-range', type=str,
                        help='Filter DAG runs by date range (e.g., "2025-03-01 to 2025-03-13")')
    
    parser.add_argument('--email-subject', type=str,
                        help='Custom email subject')
    
    parser.add_argument('--email-recipients', type=str,
                        help='Comma-separated list of email recipients (overrides environment variable)')
    
    parser.add_argument('--send-email', action='store_true',
                        help='Automatically send the email instead of saving as draft')
    
    parser.add_argument('--config', type=str,
                        help='Path to configuration file')
    
    return parser.parse_args()

def load_config(config_path=None):
    """
    Load configuration from file and/or environment variables.
    
    Args:
        config_path (str): Path to configuration file
        
    Returns:
        dict: Configuration settings
    """
    # Load environment variables from .env file (if exists)
    load_dotenv()
    
    # Default configuration from environment variables
    config = {
        # Microsoft Graph API settings
        'ms_graph_client_id': os.getenv('MS_GRAPH_CLIENT_ID'),
        'ms_graph_tenant_id': os.getenv('MS_GRAPH_TENANT_ID'),
        'ms_graph_client_secret': os.getenv('MS_GRAPH_CLIENT_SECRET'),
        
        # Composer settings
        'composer_url': os.getenv('COMPOSER_URL'),
        'dag_id': os.getenv('DAG_ID'),
        
        # Email settings
        'email_recipients': os.getenv('EMAIL_RECIPIENTS', '').split(','),
        
        # Browser settings
        'headless': False,
        
        # Filter settings
        'status_filter': None,
        'date_range': None,
        
        # Email content settings
        'email_subject': None,
        'send_email': False
    }
    
    # Load configuration from file if provided
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                
            # Update configuration with values from file
            for key, value in file_config.items():
                if key in config and value is not None:
                    config[key] = value
                    
            logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration from {config_path}: {e}")
    
    return config

def update_config_with_args(config, args):
    """
    Update configuration with command line arguments.
    
    Args:
        config (dict): Configuration settings
        args (Namespace): Command line arguments
        
    Returns:
        dict: Updated configuration settings
    """
    # Update configuration with command line arguments
    if args.headless:
        config['headless'] = True
        
    if args.dag_id:
        config['dag_id'] = args.dag_id
        
    if args.status_filter:
        config['status_filter'] = args.status_filter
        
    if args.date_range:
        config['date_range'] = args.date_range
        
    if args.email_subject:
        config['email_subject'] = args.email_subject
        
    if args.email_recipients:
        config['email_recipients'] = args.email_recipients.split(',')
        
    if args.send_email:
        config['send_email'] = True
    
    return config

def validate_config(config):
    """
    Validate configuration settings.
    
    Args:
        config (dict): Configuration settings
        
    Returns:
        bool: True if valid, False otherwise
    """
    missing_vars = []
    
    if not config['ms_graph_client_id']:
        missing_vars.append("MS_GRAPH_CLIENT_ID")
    if not config['ms_graph_tenant_id']:
        missing_vars.append("MS_GRAPH_TENANT_ID")
    if not config['ms_graph_client_secret']:
        missing_vars.append("MS_GRAPH_CLIENT_SECRET")
    if not config['composer_url']:
        missing_vars.append("COMPOSER_URL")
    if not config['dag_id']:
        missing_vars.append("DAG_ID")
    if not config['email_recipients'] or not any(config['email_recipients']):
        missing_vars.append("EMAIL_RECIPIENTS")
    
    if missing_vars:
        logger.error(f"Missing required configuration: {', '.join(missing_vars)}")
        return False
    
    return True

def run_automation(config):
    """
    Run the end-to-end automation process.
    
    Args:
        config (dict): Configuration settings
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Import required modules here to avoid circular imports
    from composer_browser_automation import ComposerBrowserAutomation
    from screenshot_email_workflow import ScreenshotEmailWorkflow
    
    # Set environment variables for components
    os.environ['MS_GRAPH_CLIENT_ID'] = config['ms_graph_client_id']
    os.environ['MS_GRAPH_TENANT_ID'] = config['ms_graph_tenant_id']
    os.environ['MS_GRAPH_CLIENT_SECRET'] = config['ms_graph_client_secret']
    os.environ['COMPOSER_URL'] = config['composer_url']
    os.environ['DAG_ID'] = config['dag_id']
    os.environ['EMAIL_RECIPIENTS'] = ','.join(config['email_recipients'])
    
    # Initialize workflow
    workflow = ScreenshotEmailWorkflow()
    
    try:
        # Initialize components
        if not workflow.initialize_graph_client():
            logger.error("Failed to initialize Microsoft Graph API client")
            return False
        
        if not workflow.initialize_browser_automation(headless=config['headless']):
            logger.error("Failed to initialize browser automation")
            return False
        
        # Capture DAG run screenshots with filtering
        logger.info(f"Capturing screenshots for DAG: {config['dag_id']}")
        logger.info(f"Filters - Status: {config['status_filter']}, Date Range: {config['date_range']}")
        
        screenshot_path, run_info = workflow.capture_dag_run_screenshots(
            status_filter=config['status_filter'],
            date_range=config['date_range']
        )
        
        if not screenshot_path or not run_info:
            logger.error("Failed to capture DAG run screenshots or get run information")
            return False
        
        logger.info(f"Screenshot captured: {screenshot_path}")
        logger.info(f"Run info: {run_info}")
        
        # Draft an email with the screenshot
        logger.info("Creating draft email with screenshot")
        draft_message = workflow.draft_email_with_screenshot(
            screenshot_path, 
            run_info,
            subject=config['email_subject']
        )
        
        if not draft_message:
            logger.error("Failed to draft email")
            return False
        
        logger.info(f"Draft email created with subject: {draft_message['subject']}")
        logger.info(f"Message ID: {draft_message['id']}")
        
        # Send the email if requested
        if config['send_email']:
            logger.info("Sending email...")
            if workflow.send_email(draft_message['id']):
                logger.info("Email sent successfully")
            else:
                logger.error("Failed to send email")
                return False
        else:
            logger.info("Email saved as draft")
        
        return True
    
    except Exception as e:
        logger.error(f"Error in automation process: {e}", exc_info=True)
        return False
    
    finally:
        # Clean up
        workflow.cleanup()
        logger.info("Automation resources cleaned up")

def main():
    """Main function to run the end-to-end automation."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Load configuration
    config = load_config(args.config)
    
    # Update configuration with command line arguments
    config = update_config_with_args(config, args)
    
    # Validate configuration
    if not validate_config(config):
        logger.error("Invalid configuration. Please check your settings.")
        return 1
    
    # Run the automation
    logger.info("Starting automation process")
    start_time = time.time()
    
    success = run_automation(config)
    
    end_time = time.time()
    duration = end_time - start_time
    
    if success:
        logger.info(f"Automation completed successfully in {duration:.2f} seconds")
        return 0
    else:
        logger.error(f"Automation failed after {duration:.2f} seconds")
        return 1

if __name__ == "__main__":
    sys.exit(main())
