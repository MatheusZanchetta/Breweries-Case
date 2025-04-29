import yaml
import logging
import os
from pyspark.sql.functions import col, lit, count
from datetime import datetime
from breweries_case.utils.spark_session import create_spark_session

# Configurar logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def AnalyticsdBrewryData(execution_date=None):
    spark = create_spark_session()
    config = load_config()

    source_path = config["source"]["path"]
    sink_path = config["sink"]["path"]

    if isinstance(execution_date, str):
        execution_date_str = execution_date
    else:
        execution_date_str = datetime.today().strftime("%Y-%m-%d")

    logger.info(f"Lendo dados existentes de {source_path}")
    df = spark.read.format("parquet").load(source_path)

    logger.info(f"Filtradando dados de {execution_date_str}")
    df_filtered = df.filter(col("ds") == lit(execution_date_str))

    logger.info("Agregando os dados")
    agg_df = (
        df_filtered.groupBy("brewery_type", "state", "country")
        .agg(count("*").alias("brewery_count"))
        .withColumn("date_execution", lit(execution_date_str))
    )

    logger.info(f"{agg_df.count()} registros novos. Salvando...")
    agg_df.write.mode("append").partitionBy("country").parquet(sink_path)

    logger.info(f"Dados agregados salvos com sucesso em {sink_path}")
    spark.stop()


if __name__ == "__main__":
    AnalyticsdBrewryData()
