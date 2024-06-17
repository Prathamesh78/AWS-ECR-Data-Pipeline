import os
import pandas as pd
from sqlalchemy import create_engine


def s3_to_df():
    """
    Read csv file from S3 to pandas DataFrame
    """
    # Get environment variables related to S3
    aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    s3_uri = os.environ.get("S3_URI")
    # Define AWS credentials for accessing S3
    aws_credentials = {
        "key": aws_access_key_id,
        "secret": aws_secret_access_key
    }
    # Read csv file from S3
    data_df = pd.read_csv(s3_uri,
                    storage_options=aws_credentials
                    )
    return data_df


def df_to_sql(data_df):
    """
    Transfer data from pandas DataFrame to MySQL table
    """
    # Get environment variables related to MySQL
    sql_host = os.environ.get("SQL_HOST")
    sql_user = os.environ.get("SQL_USER")
    sql_password = os.environ.get("SQL_PASSWORD")
    sql_db = os.environ.get("SQL_DB")
    sql_table = os.environ.get("SQL_TABLE")
    # Define connection string
    connection_string = "mysql+pymysql://{uid}:{pwd}@{host}/{db}".format(
        uid=sql_user,
        pwd=sql_password,
        host=sql_host,
        db=sql_db
    )
    # Create engine
    engine = create_engine(connection_string)
    # Transfer data from DataFrame to MySQL table
    data_df.to_sql(sql_table, con=engine, index=False, if_exists="append")


def main():
    """
    Main function which transfers the data from S3 to MySQL table
    """
    data_df = s3_to_df()
    df_to_sql(data_df)


if __name__ == "__main__":
    main()
