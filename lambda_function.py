import subprocess

def lambda_handler(event, context):
    result = subprocess.run(['python', 's3_to_rds.py'], capture_output=True, text=True)
    return {
        'statusCode': 200,
        'body': result.stdout
    }
