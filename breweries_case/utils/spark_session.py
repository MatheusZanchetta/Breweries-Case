from airflow.providers.amazon.aws.hooks.base_aws import AwsBaseHook
from pyspark.sql import SparkSession


def create_spark_session(aws_conn_id: str = "aws_default") -> SparkSession:
    """
    Cria uma SparkSession configurada para ler/escrever no S3
    usando as credenciais armazenadas no Airflow Connections.
    """

    aws_hook = AwsBaseHook(aws_conn_id=aws_conn_id, client_type="s3")
    credentials = aws_hook.get_credentials()

    spark = (
        SparkSession.builder.appName("Breweries Case - Airflow")
        .config(
            "spark.hadoop.fs.s3a.impl",
            "org.apache.hadoop.fs.s3a.S3AFileSystem",
        )
        .config(
            "spark.hadoop.fs.s3a.aws.credentials.provider",
            "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider",
        )
        .config("spark.hadoop.fs.s3a.access.key", credentials.access_key)
        .config("spark.hadoop.fs.s3a.secret.key", credentials.secret_key)
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .getOrCreate()
    )

    return spark
