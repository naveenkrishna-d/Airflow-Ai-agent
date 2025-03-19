# Python Automation Requirements

This document outlines the requirements for each technology component in our automation project.

## Microsoft Graph API
- **Purpose**: Draft and send emails via Outlook
- **Dependencies**:
  - `azure-identity`: For authentication with Azure AD
  - `msgraph-sdk-python`: Microsoft Graph SDK for Python
- **Authentication**: Client credentials flow with Azure AD app registration
- **Required Permissions**: Mail.Send, Mail.ReadWrite, User.Read.All

## Google Auth & GCP SDK
- **Purpose**: Authenticate and interact with Google Cloud services
- **Dependencies**:
  - `google-auth`: Authentication library for Google APIs
  - `google-api-python-client`: Google API client library
  - `google-cloud-storage`: For Cloud Storage operations (if needed)
  - `google-cloud-bigquery`: For BigQuery operations (if needed)
- **Authentication**: Application Default Credentials (ADC) or service account

## Airflow (Composer)
- **Purpose**: Orchestrate tasks and workflows
- **Dependencies**:
  - `apache-airflow`: Core Airflow package
  - `google-cloud-composer`: For interacting with Cloud Composer
  - `apache-airflow-providers-google`: Airflow providers for Google Cloud
  - `apache-airflow-providers-microsoft-azure`: Airflow providers for Microsoft services
- **Authentication**: Service account for GCP, client credentials for Microsoft Graph

## Combined Environment
- Python 3.10+ (compatible with all required libraries)
- Virtual environment for dependency isolation
- Configuration management for storing credentials securely
