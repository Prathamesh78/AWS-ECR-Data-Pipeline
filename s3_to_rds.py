import boto3
import pandas as pd
import psycopg2
import os

# AWS Credentials
aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
aws_region = os.environ['AWS_REGION']
s3_bucket = os.environ['S3_BUCKET']
s3_key = os.environ['S3_KEY']

# RDS Credentials
rds_host = os.environ['RDS_HOST']
rds_port = os.environ['RDS_PORT']
rds_user = os.environ['RDS_USER']
rds_password = os.environ['RDS_PASSWORD']
rds_db = os.environ['RDS_DB']
rds_table = os.environ['RDS_TABLE']

# Initialize S3 client
s3_client = boto3.client('s3', 
                         aws_access_key_id=aws_access_key_id, 
                         aws_secret_access_key=aws_secret_access_key, 
                         region_name=aws_region)

# Download file from S3
s3_client.download_file(s3_bucket, s3_key, '/tmp/data.csv')

# Load data into pandas DataFrame
df = pd.read_csv('/tmp/data.csv')

# Connect to RDS
conn = psycopg2.connect(
    host=rds_host,
    port=rds_port,
    user=rds_user,
    password=rds_password,
    dbname=rds_db
)
cur = conn.cursor()

# Insert data into RDS table
for index, row in df.iterrows():
    cur.execute(f"INSERT INTO {rds_table} (column1, column2, ...) VALUES (%s, %s, ...)", tuple(row))

conn.commit()
cur.close()
conn.close()

print("Data transferred successfully!")
