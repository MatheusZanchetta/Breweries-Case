# Cloud Access Instructions

To interact with our S3 buckets (`mzan-raw-breweries-case`, `mzan-curated-breweries-case`, `mzan-analytics-breweries-case`) via your Airflow DAGs:

## Using Your AWS Account
I have granted access to your AWS Account . You can use a role or IAM user from your account to interact with my buckets.

Ensure your AWS credentials (via environment variables or an Airflow connection) are properly set.

Required Permissions:
- s3:GetObject
- s3:PutObject
- s3:DeleteObject

Bucket Names:
- `mzan-raw-breweries-case`
- `mzan-curated-breweries-case`
- `mzan-analytics-breweries-case`
