"""
Selenium Browser Automation for Google Managed Composer
-----------------------------------------------------
This script demonstrates how to use Selenium to automate browser interactions
with Google Managed Composer (Airflow) to capture screenshots of DAG runs.
"""

import os
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# Load environment variables from .env file (if exists)
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ComposerBrowserAutomation:
    def __init__(self, headless=False):
        """
        Initialize the browser automation for Google Managed Composer.
        
        Args:
            headless (bool): Whether to run the browser in headless mode
        """
        self.headless = headless
        self.driver = None
        self.screenshots_dir = os.path.join(os.getcwd(), "screenshots")
        
        # Create screenshots directory if it doesn't exist
        if not os.path.exists(self.screenshots_dir):
            os.makedirs(self.screenshots_dir)
    
    def setup_driver(self):
        """Set up the Chrome WebDriver with appropriate options."""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Chrome WebDriver set up successfully")
            return True
        except Exception as e:
            logger.error(f"Error setting up Chrome WebDriver: {e}")
            return False
    
    def login_to_composer(self, composer_url, wait_time=60):
        """
        Login to Google Managed Composer using Google authentication.
        
        Args:
            composer_url (str): URL of the Composer environment
            wait_time (int): Maximum time to wait for authentication
            
        Returns:
            bool: True if login successful, False otherwise
        """
        if not self.driver:
            logger.error("WebDriver not initialized. Call setup_driver() first.")
            return False
        
        try:
            logger.info(f"Navigating to Composer URL: {composer_url}")
            self.driver.get(composer_url)
            
            # Wait for Google authentication to complete
            # This assumes the user is already authenticated with Google in the browser
            # or that authentication happens automatically
            logger.info(f"Waiting up to {wait_time} seconds for authentication...")
            
            # Wait for Airflow UI to load (looking for the Airflow logo)
            WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".navbar-brand"))
            )
            
            logger.info("Successfully logged in to Composer")
            return True
        except TimeoutException:
            logger.error("Timeout waiting for authentication or Airflow UI to load")
            self.take_screenshot("login_timeout")
            return False
        except Exception as e:
            logger.error(f"Error during login: {e}")
            self.take_screenshot("login_error")
            return False
    
    def navigate_to_dag_runs(self, dag_id):
        """
        Navigate to the DAG runs page for a specific DAG.
        
        Args:
            dag_id (str): ID of the DAG to view
            
        Returns:
            bool: True if navigation successful, False otherwise
        """
        if not self.driver:
            logger.error("WebDriver not initialized. Call setup_driver() first.")
            return False
        
        try:
            # Navigate to the DAG details page
            dag_url = f"{self.driver.current_url.split('?')[0]}/tree?dag_id={dag_id}"
            logger.info(f"Navigating to DAG page: {dag_url}")
            self.driver.get(dag_url)
            
            # Wait for the page to load
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, "dag"))
            )
            
            # Click on the "DAG Runs" tab
            runs_tab = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'DAG Runs')]"))
            )
            runs_tab.click()
            
            # Wait for the DAG runs table to load
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".dag-runs-table"))
            )
            
            logger.info(f"Successfully navigated to DAG runs for {dag_id}")
            return True
        except TimeoutException:
            logger.error("Timeout waiting for DAG runs page to load")
            self.take_screenshot("dag_runs_timeout")
            return False
        except Exception as e:
            logger.error(f"Error navigating to DAG runs: {e}")
            self.take_screenshot("dag_runs_error")
            return False
    
    def filter_dag_runs(self, status=None, date_range=None):
        """
        Apply filters to the DAG runs view.
        
        Args:
            status (str): Filter by run status (e.g., 'success', 'failed')
            date_range (str): Filter by date range
            
        Returns:
            bool: True if filtering successful, False otherwise
        """
        if not self.driver:
            logger.error("WebDriver not initialized. Call setup_driver() first.")
            return False
        
        try:
            # Open the filter dropdown
            filter_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".filter-btn"))
            )
            filter_button.click()
            
            # Apply status filter if provided
            if status:
                status_dropdown = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "select[name='status']"))
                )
                status_dropdown.click()
                
                status_option = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"//option[contains(text(), '{status}')]"))
                )
                status_option.click()
            
            # Apply date range filter if provided
            if date_range:
                date_input = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='date_range']"))
                )
                date_input.clear()
                date_input.send_keys(date_range)
            
            # Apply the filters
            apply_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".apply-btn"))
            )
            apply_button.click()
            
            # Wait for the filtered results to load
            time.sleep(5)
            
            logger.info(f"Successfully applied filters: status={status}, date_range={date_range}")
            return True
        except TimeoutException:
            logger.error("Timeout waiting for filter elements")
            self.take_screenshot("filter_timeout")
            return False
        except Exception as e:
            logger.error(f"Error applying filters: {e}")
            self.take_screenshot("filter_error")
            return False
    
    def get_last_dag_run(self):
        """
        Get information about the last DAG run.
        
        Returns:
            dict: Information about the last DAG run, or None if not found
        """
        if not self.driver:
            logger.error("WebDriver not initialized. Call setup_driver() first.")
            return None
        
        try:
            # Find the first row in the DAG runs table
            first_row = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".dag-runs-table tbody tr:first-child"))
            )
            
            # Extract information from the row
            run_id = first_row.find_element(By.CSS_SELECTOR, "td:nth-child(1)").text
            run_type = first_row.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text
            execution_date = first_row.find_element(By.CSS_SELECTOR, "td:nth-child(3)").text
            start_date = first_row.find_element(By.CSS_SELECTOR, "td:nth-child(4)").text
            end_date = first_row.find_element(By.CSS_SELECTOR, "td:nth-child(5)").text
            status = first_row.find_element(By.CSS_SELECTOR, "td:nth-child(6)").text
            
            run_info = {
                "run_id": run_id,
                "run_type": run_type,
                "execution_date": execution_date,
                "start_date": start_date,
                "end_date": end_date,
                "status": status
            }
            
            logger.info(f"Retrieved last DAG run information: {run_info}")
            return run_info
        except TimeoutException:
            logger.error("Timeout waiting for DAG runs table")
            self.take_screenshot("last_run_timeout")
            return None
        except NoSuchElementException:
            logger.error("No DAG runs found in the table")
            self.take_screenshot("no_dag_runs")
            return None
        except Exception as e:
            logger.error(f"Error getting last DAG run: {e}")
            self.take_screenshot("last_run_error")
            return None
    
    def take_screenshot(self, name_prefix=None):
        """
        Take a screenshot of the current browser window.
        
        Args:
            name_prefix (str): Prefix for the screenshot filename
            
        Returns:
            str: Path to the saved screenshot, or None if failed
        """
        if not self.driver:
            logger.error("WebDriver not initialized. Call setup_driver() first.")
            return None
        
        try:
            # Generate a filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prefix = f"{name_prefix}_" if name_prefix else ""
            filename = f"{prefix}{timestamp}.png"
            filepath = os.path.join(self.screenshots_dir, filename)
            
            # Take the screenshot
            self.driver.save_screenshot(filepath)
            logger.info(f"Screenshot saved to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return None
    
    def close(self):
        """Close the WebDriver and release resources."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("WebDriver closed")


def main():
    """Main function to demonstrate Composer browser automation."""
    # Get Composer URL from environment variable or use a default
    composer_url = os.getenv("COMPOSER_URL")
    dag_id = os.getenv("DAG_ID")
    
    if not composer_url:
        logger.error("COMPOSER_URL environment variable not set")
        print("Please set the COMPOSER_URL environment variable")
        return
    
    if not dag_id:
        logger.error("DAG_ID environment variable not set")
        print("Please set the DAG_ID environment variable")
        return
    
    # Initialize browser automation
    automation = ComposerBrowserAutomation(headless=False)
    
    try:
        # Set up the WebDriver
        if not automation.setup_driver():
            logger.error("Failed to set up WebDriver")
            return
        
        # Login to Composer
        if not automation.login_to_composer(composer_url):
            logger.error("Failed to login to Composer")
            return
        
        # Navigate to DAG runs
        if not automation.navigate_to_dag_runs(dag_id):
            logger.error(f"Failed to navigate to DAG runs for {dag_id}")
            return
        
        # Apply filters (optional)
        automation.filter_dag_runs(status="success")
        
        # Take a screenshot of the filtered DAG runs
        screenshot_path = automation.take_screenshot("filtered_dag_runs")
        
        # Get information about the last DAG run
        last_run = automation.get_last_dag_run()
        
        if last_run:
            print("\nLast DAG Run Information:")
            for key, value in last_run.items():
                print(f"{key}: {value}")
        
        if screenshot_path:
            print(f"\nScreenshot saved to: {screenshot_path}")
    
    finally:
        # Clean up
        automation.close()


if __name__ == "__main__":
    main()
