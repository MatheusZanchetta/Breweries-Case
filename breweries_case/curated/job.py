import yaml
import logging
import os
from pyspark.sql.functions import col, lit

from breweries_case.utils.spark_session import create_spark_session

# Configurar logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def CuratedBrewryData(execution_date=None):
    config = load_config()

    spark = create_spark_session()

    logger.info("SparkSession iniciada.")

    if isinstance(execution_date, str):
        execution_date_str = execution_date
    else:
        execution_date_str = execution_date.strftime("%Y-%m-%d")

    source_path = config["source"]["path"]
    sink_path = config["sink"]["path"]

    logger.info(f"Lendo dados existentes de {source_path}")
    existing_df = spark.read.json(source_path)
    logger.info(f"Filtradando dados de {execution_date_str}")
    filtered_df = existing_df.filter(
        col("date_execution") == lit(execution_date_str)
    )
    logger.info(
        f"Encontrados {filtered_df.count()} registros novos. Salvando..."
    )
    filtered_df.write.mode("append").partitionBy("country").parquet(sink_path)
    logger.info("Salvo com Sucesso")


if __name__ == "__main__":
    CuratedBrewryData()
