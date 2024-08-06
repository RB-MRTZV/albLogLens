# albReports

everages AWS serverless technologies to create an automated, scalable solution for ALB log analysis. Here's what makes it special:

Automated Queries: Daily execution of predefined Athena queries against your ALB logs

Persistent Storage: Results stored in DynamoDB for quick retrieval and historical analysis

API Access: Easy retrieval of query results through API Gateway

Visualization: Simple web interface to view and interact with the data

Serverless Architecture: Utilising AWS Lambda, S3, DynamoDB, and API Gateway for a scalable, cost-effective solution

Solution Architecture

Let's break down the key components of our serverless application:

S3 Bucket (AthenaQueryResultS3Bucket): Stores the results of our Athena queries

API Gateway (albResultsAPI): Provides an HTTP endpoint to retrieve query results

Lambda Function (albReports): Executes Athena queries and stores results in DynamoDB

DynamoDB Table (QueryResultsTable): Stores query results for fast retrieval

Lambda Function (RetrieveQueryResults): Fetches data from DynamoDB when called via API Gateway


The application works as follows:

The albReports Lambda function runs daily, executing predefined Athena queries against your ALB logs

Query results are stored in both S3 and DynamoDB

The RetrieveQueryResults Lambda function can be called via API Gateway to fetch the latest results

A simple web interface visualises the data retrieved from the API

Prerequisites

Before deploying this solution, ensure you have the following:

An existing Athena Database

An Athena Table with partitioning enabled for your ALB logs

An S3 bucket that stores your ALB logs

SAM CLI installed on your local machine

AWS CLI and permissions to deploy the resources

These prerequisites ensure that you have the necessary infrastructure in place to query your ALB logs and deploy the serverless application.

Deployment Instructions

Ready to simplify your ALB log analysis? Follow these steps to deploy the application:

Clone the repository to your local machine : https://github.com/RB-MRTZV/albLogLens.git

Open the template.yaml file and make the following changes:

      Replace Athena_DB_Name with your Athena database name

      Update Athena_Table_Name to match your ALB logs table

      Set Query_Period_In_Days to your desired query range.    

      Replace the S3 bucket ARN with your ALB logs bucket

      Choose a unique name for the AthenaQueryResultS3Bucket


Open a terminal and navigate to the project directory

Run the following commands:

sam build --use-container

sam deploy

  5.  Monitor the deployment progress in your CLI and AWS CloudFormation console

  6.  Once deployed, manually run the albReports Lambda function to generate initial results

7.   Replace your API Endpoint in the index.html

8 .  Open the index.html file locally to view your ALB log insights

Enhancing Security with API Keys

To protect your API from unauthorised access and potential abuse, it's crucial to implement API key authentication. This section will guide you through the process of adding API key security to your deployment.

Why Use API Keys?

API keys offer several benefits:

Access Control: Only clients with a valid API key can make requests

Usage Tracking: Monitor and analyse API usage per key

Throttling: Implement rate limiting to prevent abuse

Implementing API Key Security

Follow these steps to add API key protection to your ALB log analysis API:

Open the templatewithApiKey.yaml file in your project directory, and follow the instructions. 

Build and deploy the template using SAM CLI: 

sam build --use-container

sam deploy

After deployment, retrieve your API key from the AWS Console or using the AWS CLI: 

aws apigateway get-api-keys --include-values

Updating the Frontend

To use the API key in your requests, you'll need to update the index.html file:

Open index.html in your text editor.

Locate the fetch function or wherever you're making API calls.

Replace 'YOUR_API_KEY_HERE' with the actual API key you retrieved earlier.

Security Considerations

Keep your API key secure and don't expose it in public repositories.

For production use, consider implementing a more robust authentication system, such as OAuth or JWT.

Regularly rotate your API keys to minimise the impact of potential key exposure.

By implementing API key security, you've significantly enhanced the protection of your ALB log analysis solution. This ensures that only authorised users can access your valuable insights while also providing you with better control and monitoring capabilities.
