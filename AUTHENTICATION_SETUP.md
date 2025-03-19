# Microsoft Graph API and Google Cloud Platform Authentication Setup

This guide provides instructions for setting up authentication for Microsoft Graph API and Google Cloud Platform services.

## Microsoft Graph API Authentication

### Prerequisites
- Microsoft Azure account
- Registered application in Azure Active Directory

### Steps to Register an Application

1. Sign in to the [Azure Portal](https://portal.azure.com/)
2. Navigate to **Azure Active Directory** > **App registrations**
3. Click **New registration**
4. Enter a name for your application
5. Select the appropriate supported account types
6. Click **Register**

### Configure API Permissions

1. In your registered application, go to **API permissions**
2. Click **Add a permission**
3. Select **Microsoft Graph**
4. Choose **Application permissions**
5. Add the following permissions:
   - Mail.ReadWrite
   - Mail.Send
6. Click **Add permissions**
7. Click **Grant admin consent** (requires admin privileges)

### Create a Client Secret

1. In your registered application, go to **Certificates & secrets**
2. Click **New client secret**
3. Enter a description and select an expiration period
4. Click **Add**
5. **Important**: Copy the secret value immediately (you won't be able to see it again)

### Get Your Application (Client) ID and Tenant ID

1. In your registered application overview page, note the **Application (client) ID**
2. Also note the **Directory (tenant) ID**

### Update Your .env File

Add the following to your `.env` file:

```
MS_GRAPH_CLIENT_ID=your_client_id
MS_GRAPH_TENANT_ID=your_tenant_id
MS_GRAPH_CLIENT_SECRET=your_client_secret
```

## Google Cloud Platform Authentication

### Prerequisites
- Google Cloud Platform account
- Project with necessary APIs enabled (Composer, Storage, etc.)

### Create a Service Account

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **IAM & Admin** > **Service Accounts**
3. Click **Create Service Account**
4. Enter a name and description for the service account
5. Click **Create and Continue**
6. Assign the following roles:
   - Composer User
   - Storage Object Viewer
   - Any other roles needed for your specific use case
7. Click **Continue** and then **Done**

### Create a Service Account Key

1. In the Service Accounts list, find your service account
2. Click the three dots menu and select **Manage keys**
3. Click **Add Key** > **Create new key**
4. Select **JSON** as the key type
5. Click **Create**
6. The key file will be downloaded to your computer

### Set Up Application Default Credentials

For local development:

```bash
gcloud auth application-default login
```

For production environments, set the environment variable:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-service-account-key.json"
```

### Enable Required APIs

Make sure the following APIs are enabled in your Google Cloud project:

```bash
gcloud services enable composer.googleapis.com
gcloud services enable storage-api.googleapis.com
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable aiplatform.googleapis.com
```

## Composer (Airflow) URL

To get your Composer environment URL:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **Composer**
3. Click on your Composer environment
4. Copy the **Airflow web server URL**

Add this to your `.env` file:

```
COMPOSER_URL=https://your-composer-environment-url
```

## Testing Your Authentication

### Test Microsoft Graph API Authentication

Run the following script:

```bash
python microsoft_graph_example.py
```

### Test Google Cloud Authentication

Run the following script:

```bash
python google_cloud_auth.py
```

## Troubleshooting

### Microsoft Graph API Issues

- Ensure your application has the correct permissions
- Verify your client ID, tenant ID, and client secret
- Check if admin consent has been granted for the required permissions

### Google Cloud Issues

- Ensure your service account has the necessary roles
- Verify the GOOGLE_APPLICATION_CREDENTIALS environment variable is set correctly
- Check if the required APIs are enabled in your project
