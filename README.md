# AWS-Serverless-Feedback-Collector

A serverless CRUD application that collects user feedback via a web form and displays recent entries on an admin page. Built entirely on AWS using serverless technologies.

---

## 🏗️ Architecture
![Alt Text](https://github.com/Naveen15github/AWS-Serverless-Feedback-Collector/blob/cd096fe9f7fa9cd7c41cde17c098eb39ecce8104/Gemini_Generated_Image_3k23fe3k23fe3k23.png)

> 📌 Architecture Diagram

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Static Hosting | AWS S3 (Static Website) |
| API Layer | AWS API Gateway v2 (HTTP API) |
| Compute | AWS Lambda (Python 3.11) |
| Database | AWS DynamoDB (On-demand) |
| Monitoring | AWS CloudWatch Logs |
| IAM | Custom Role with least-privilege policies |

---

## 📸 Screenshots

### Frontend — Submit Feedback Form
![Alt Text](https://github.com/Naveen15github/AWS-Serverless-Feedback-Collector/blob/cd096fe9f7fa9cd7c41cde17c098eb39ecce8104/Screenshot%20(530).png)

### Frontend — Feedback Saved Confirmation
![Alt Text](https://github.com/Naveen15github/AWS-Serverless-Feedback-Collector/blob/cd096fe9f7fa9cd7c41cde17c098eb39ecce8104/Screenshot%20(531).png)

### Frontend — Admin View with Loaded Entries
![Alt Text](https://github.com/Naveen15github/AWS-Serverless-Feedback-Collector/blob/cd096fe9f7fa9cd7c41cde17c098eb39ecce8104/Screenshot%20(532).png)

### AWS Console — DynamoDB Table Items
![Alt Text](https://github.com/Naveen15github/AWS-Serverless-Feedback-Collector/blob/cd096fe9f7fa9cd7c41cde17c098eb39ecce8104/Screenshot%20(533).png)

### AWS Console — API Gateway Routes
![Alt Text](https://github.com/Naveen15github/AWS-Serverless-Feedback-Collector/blob/cd096fe9f7fa9cd7c41cde17c098eb39ecce8104/Screenshot%20(534).png)

### AWS Console — Lambda Functions
![Alt Text](https://github.com/Naveen15github/AWS-Serverless-Feedback-Collector/blob/cd096fe9f7fa9cd7c41cde17c098eb39ecce8104/Screenshot%20(535).png)

---

## 📁 Project Structure
```
serverless-feedback-collector/
│
├── post_feedback.py       # Lambda function — POST /feedback
├── get_feedback.py        # Lambda function — GET /admin/feedback
├── post_feedback.zip      # Deployment package for PostFeedback
├── get_feedback.zip       # Deployment package for GetFeedback
├── index.html             # Frontend (S3 static site)
├── trust.json             # IAM role trust policy
├── bucket-policy.json     # S3 public access policy
└── README.md
```

---

## ⚙️ AWS Resources Created

| Resource | Name | Details |
|---|---|---|
| DynamoDB Table | `FeedbackTable` | Partition key: `id` (String) |
| IAM Role | `LambdaDynamoRole` | Lambda execution role |
| Lambda Function | `PostFeedback` | Python 3.11, handles POST |
| Lambda Function | `GetFeedback` | Python 3.11, handles GET |
| API Gateway | `FeedbackAPI` | HTTP API, prod stage |
| S3 Bucket | `feedback-app-478468758108` | Static website hosting |

---

## 🚀 Deployment Steps

### Prerequisites
- AWS CLI installed and configured
- AWS account with sufficient permissions
- PowerShell (Windows)

---

### Step 1 — Create DynamoDB Table
```powershell
aws dynamodb create-table `
  --table-name FeedbackTable `
  --attribute-definitions AttributeName=id,AttributeType=S `
  --key-schema AttributeName=id,KeyType=HASH `
  --billing-mode PAY_PER_REQUEST `
  --region ap-south-1
```

**What this does:** Creates a DynamoDB table with `id` as the primary key using on-demand billing (no capacity planning needed).

---

### Step 2 — Create IAM Role for Lambda

Create the trust policy file:
```powershell
'{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}' | Out-File -FilePath trust.json -Encoding ascii
```

Create the IAM role:
```powershell
aws iam create-role `
  --role-name LambdaDynamoRole `
  --assume-role-policy-document file://trust.json
```

Attach permissions:
```powershell
aws iam attach-role-policy `
  --role-name LambdaDynamoRole `
  --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

aws iam attach-role-policy `
  --role-name LambdaDynamoRole `
  --policy-arn arn:aws:iam::aws:policy/CloudWatchLogsFullAccess
```

**What this does:** Creates a least-privilege IAM role that allows Lambda to read/write DynamoDB and write logs to CloudWatch.

---

### Step 3 — Create Lambda Functions

**post_feedback.py**
```python
import json, boto3, uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('FeedbackTable')

def handler(event, context):
    body = json.loads(event.get('body', '{}'))
    if not body.get('name') or not body.get('message'):
        return {
            'statusCode': 400,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Name and message are required'})
        }
    item = {
        'id': str(uuid.uuid4()),
        'name': body['name'],
        'email': body.get('email', ''),
        'message': body['message'],
        'timestamp': datetime.utcnow().isoformat()
    }
    table.put_item(Item=item)
    return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'message': 'Feedback saved!'})
    }
```

**get_feedback.py**
```python
import json, boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('FeedbackTable')

def handler(event, context):
    result = table.scan(Limit=50)
    items = sorted(
        result.get('Items', []),
        key=lambda x: x.get('timestamp', ''),
        reverse=True
    )
    return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps(items)
    }
```

Zip and deploy:
```powershell
Compress-Archive -Path post_feedback.py -DestinationPath post_feedback.zip
Compress-Archive -Path get_feedback.py -DestinationPath get_feedback.zip

aws lambda create-function `
  --function-name PostFeedback `
  --runtime python3.11 `
  --role arn:aws:iam::478468758108:role/LambdaDynamoRole `
  --handler post_feedback.handler `
  --zip-file fileb://post_feedback.zip `
  --region ap-south-1

aws lambda create-function `
  --function-name GetFeedback `
  --runtime python3.11 `
  --role arn:aws:iam::478468758108:role/LambdaDynamoRole `
  --handler get_feedback.handler `
  --zip-file fileb://get_feedback.zip `
  --region ap-south-1
```

Grant API Gateway permission to invoke Lambda:
```powershell
aws lambda add-permission `
  --function-name PostFeedback `
  --statement-id apigateway-post `
  --action lambda:InvokeFunction `
  --principal apigateway.amazonaws.com `
  --region ap-south-1

aws lambda add-permission `
  --function-name GetFeedback `
  --statement-id apigateway-get `
  --action lambda:InvokeFunction `
  --principal apigateway.amazonaws.com `
  --region ap-south-1
```

---

### Step 4 — Create API Gateway

Create the HTTP API:
```powershell
aws apigatewayv2 create-api `
  --name FeedbackAPI `
  --protocol-type HTTP `
  --cors-configuration AllowOrigins="*",AllowMethods="GET,POST,OPTIONS",AllowHeaders="Content-Type" `
  --region ap-south-1
```

Create integrations (replace `YOUR_API_ID` with actual ID from above output):
```powershell
aws apigatewayv2 create-integration `
  --api-id YOUR_API_ID `
  --integration-type AWS_PROXY `
  --integration-uri arn:aws:lambda:ap-south-1:478468758108:function:PostFeedback `
  --payload-format-version 2.0 `
  --region ap-south-1

aws apigatewayv2 create-integration `
  --api-id YOUR_API_ID `
  --integration-type AWS_PROXY `
  --integration-uri arn:aws:lambda:ap-south-1:478468758108:function:GetFeedback `
  --payload-format-version 2.0 `
  --region ap-south-1
```

Create routes (replace integration IDs from above outputs):
```powershell
aws apigatewayv2 create-route `
  --api-id YOUR_API_ID `
  --route-key "POST /feedback" `
  --target integrations/POST_INTEGRATION_ID `
  --region ap-south-1

aws apigatewayv2 create-route `
  --api-id YOUR_API_ID `
  --route-key "GET /admin/feedback" `
  --target integrations/GET_INTEGRATION_ID `
  --region ap-south-1
```

Deploy to prod stage:
```powershell
aws apigatewayv2 create-stage `
  --api-id YOUR_API_ID `
  --stage-name prod `
  --auto-deploy `
  --region ap-south-1
```

**What this does:** Creates an HTTP API with CORS enabled, connects both routes to their respective Lambda functions, and deploys to a `prod` stage.

---

### Step 5 — Deploy Frontend to S3

Create the S3 bucket:
```powershell
aws s3api create-bucket `
  --bucket feedback-app-478468758108 `
  --region ap-south-1 `
  --create-bucket-configuration LocationConstraint=ap-south-1
```

Enable static website hosting:
```powershell
aws s3 website s3://feedback-app-478468758108/ --index-document index.html
```

Make bucket public:
```powershell
'{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":"*","Action":"s3:GetObject","Resource":"arn:aws:s3:::feedback-app-478468758108/*"}]}' | Out-File -FilePath bucket-policy.json -Encoding ascii

aws s3api put-public-access-block `
  --bucket feedback-app-478468758108 `
  --public-access-block-configuration BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false

aws s3api put-bucket-policy `
  --bucket feedback-app-478468758108 `
  --policy file://bucket-policy.json
```

Upload the HTML file:
```powershell
aws s3 cp index.html s3://feedback-app-478468758108/ --content-type text/html
```
---

## 🧪 Testing

### Test via Browser
1. Open the S3 website URL
2. Fill in Name, Email, Message → click **Submit**
3. Expected: "Feedback saved!" confirmation
4. Click **Load Feedback** → entries appear below

### Test via PowerShell

**POST:**
```powershell
Invoke-RestMethod `
  -Uri "https://846n061vm1.execute-api.ap-south-1.amazonaws.com/prod/feedback" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"name":"Test User","email":"test@test.com","message":"Hello!"}'
```

**GET:**
```powershell
Invoke-RestMethod `
  -Uri "https://846n061vm1.execute-api.ap-south-1.amazonaws.com/prod/admin/feedback" `
  -Method GET
```

**Scan DynamoDB directly:**
```powershell
aws dynamodb scan --table-name FeedbackTable --region ap-south-1
```


---

## 📊 DynamoDB Schema

| Attribute | Type | Description |
|---|---|---|
| `id` | String (PK) | UUID generated by Lambda |
| `name` | String | Submitted by user |
| `email` | String | Optional, submitted by user |
| `message` | String | Feedback text |
| `timestamp` | String | UTC ISO format, set by Lambda |

---

## 🔒 Security Notes

- IAM role follows least-privilege principle — only DynamoDB and CloudWatch access
- CORS is configured to allow all origins (`*`) — restrict to your domain in production
- Admin route has no authentication — add AWS Cognito for production use
- S3 bucket is publicly readable — suitable for static assets only

---

## 📈 Monitoring

CloudWatch log groups are auto-created for both Lambda functions:
- `/aws/lambda/PostFeedback`
- `/aws/lambda/GetFeedback`

View logs:
```powershell
aws logs tail /aws/lambda/PostFeedback --region ap-south-1
aws logs tail /aws/lambda/GetFeedback --region ap-south-1
```

---

## 🧹 Cleanup (Delete All Resources)
```powershell
# Delete Lambda functions
aws lambda delete-function --function-name PostFeedback --region ap-south-1
aws lambda delete-function --function-name GetFeedback --region ap-south-1

# Delete API Gateway
aws apigatewayv2 delete-api --api-id 846n061vm1 --region ap-south-1

# Delete DynamoDB table
aws dynamodb delete-table --table-name FeedbackTable --region ap-south-1

# Empty and delete S3 bucket
aws s3 rm s3://feedback-app-478468758108 --recursive
aws s3api delete-bucket --bucket feedback-app-478468758108 --region ap-south-1

# Delete IAM role
aws iam detach-role-policy --role-name LambdaDynamoRole --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
aws iam detach-role-policy --role-name LambdaDynamoRole --policy-arn arn:aws:iam::aws:policy/CloudWatchLogsFullAccess
aws iam delete-role --role-name LambdaDynamoRole
```

---

## 👤 Author

**Naveen G**  
Built as a hands-on AWS serverless project to learn cloud-native architecture, Lambda, DynamoDB, API Gateway, and S3 static hosting.
