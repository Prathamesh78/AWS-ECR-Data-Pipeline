import boto3
import pymysql
import os

s3 = boto3.client('s3')
rds = boto3.client('rds')
glue = boto3.client('glue')

def read_from_s3(bucket_name, key):
    obj = s3.get_object(Bucket=bucket_name, Key=key)
    data = obj['Body'].read().decode('utf-8')
    return data

def push_to_rds(data):
    try:
        connection = pymysql.connect(
            host=os.getenv('RDS_HOST'),
            user=os.getenv('RDS_USER'),
            password=os.getenv('RDS_PASSWORD'),
            db=os.getenv('RDS_DB')
        )
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO your_table (column_name) VALUES (%s)", (data,))
        connection.commit()
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        connection.close()
    return True

def push_to_glue(data):
    try:
        # Add your Glue logic here
        pass
    except Exception as e:
        print(f"Error: {e}")
        return False
    return True

def main():
    bucket_name = os.getenv('S3_BUCKET')
    key = os.getenv('S3_KEY')

    data = read_from_s3(bucket_name, key)
    if not push_to_rds(data):
        push_to_glue(data)

if __name__ == "__main__":
    main()
