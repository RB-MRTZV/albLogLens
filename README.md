# ALB Log Lens

ALB Log Lens is a serverless solution for automated Application Load Balancer (ALB) log analysis using AWS technologies. This project simplifies the process of gaining insights from your ALB logs by providing automated queries, persistent storage, and easy data visualization.

## Features

- **Automated Queries**: Daily execution of predefined Athena queries against your ALB logs
- **Persistent Storage**: Results stored in DynamoDB for quick retrieval and historical analysis
- **API Access**: Easy retrieval of query results through API Gateway
- **Visualization**: Simple web interface to view and interact with the data
- **Serverless Architecture**: Utilizing AWS Lambda, S3, DynamoDB, and API Gateway for a scalable, cost-effective solution

## Solution Architecture

The serverless application consists of the following key components:

- S3 Bucket (AthenaQueryResultS3Bucket): Stores the results of Athena queries
- API Gateway (albResultsAPI): Provides an HTTP endpoint to retrieve query results
- Lambda Function (albReports): Executes Athena queries and stores results in DynamoDB
- DynamoDB Table (QueryResultsTable): Stores query results for fast retrieval
- Lambda Function (RetrieveQueryResults): Fetches data from DynamoDB when called via API Gateway

## Prerequisites

Before deploying this solution, ensure you have:

- An existing Athena Database
- An Athena Table with partitioning enabled for your ALB logs
- An S3 bucket that stores your ALB logs
- SAM CLI installed on your local machine
- AWS CLI and permissions to deploy the resources

## Deployment Instructions

1. Clone the repository:
   ```
   git clone https://github.com/RB-MRTZV/albLogLens.git
   ```

2. Open the `template.yaml` file and make the following changes:
   - Replace `Athena_DB_Name` with your Athena database name
   - Update `Athena_Table_Name` to match your ALB logs table
   - Set `Query_Period_In_Days` to your desired query range
   - Replace the S3 bucket ARN with your ALB logs bucket
   - Choose a unique name for the `AthenaQueryResultS3Bucket`

3. Open a terminal and navigate to the project directory

4. Run the following commands:
   ```
   sam build --use-container
   sam deploy
   ```

5. Monitor the deployment progress in your CLI and AWS CloudFormation console

6. Once deployed, manually run the `albReports` Lambda function to generate initial results

7. Replace your API Endpoint in the `index.html`

8. Open the `index.html` file locally to view your ALB log insights

## Enhancing Security with API Keys

To protect your API from unauthorized access, you can implement API key authentication:

1. Open the `templatewithApiKey.yaml` file and follow the instructions.

2. Build and deploy the template:
   ```
   sam build --use-container
   sam deploy
   ```

3. Retrieve your API key:
   ```
   aws apigateway get-api-keys --include-values
   ```

4. Update the `index.html` file:
   - Locate the `fetch` function or wherever you're making API calls
   - Replace `'YOUR_API_KEY_HERE'` with the actual API key you retrieved

### Security Considerations

- Keep your API key secure and don't expose it in public repositories
- For production use, consider implementing a more robust authentication system, such as OAuth or JWT
- Regularly rotate your API keys to minimize the impact of potential key exposure

## Conclusion

ALB Log Lens provides a scalable, cost-effective way to gain visibility into your application's traffic patterns and performance. By leveraging AWS services like Lambda, Athena, and DynamoDB, this solution automates the process of ALB log analysis and provides valuable insights.

## Contributing

Feel free to contribute to the project on GitHub or reach out with questions and suggestions.
