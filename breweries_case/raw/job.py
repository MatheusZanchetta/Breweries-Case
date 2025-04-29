import yaml
import logging
import os
import json
import requests
from pyspark.sql.functions import col, lit

from breweries_case.utils.spark_session import create_spark_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def fetch_brewery_from_api(execution_date=None):
    api_url = "https://api.openbrewerydb.org/v1/breweries"
    per_page = 50
    page = 1
    all_breweries = []
    try:
        logger.info(f"Buscando dados da API: {api_url}")
        while True:
            response = requests.get(
                api_url,
                params={"per_page": per_page, "page": page},
                timeout=20,
            )
            data = response.json()
            if not data:
                break
            all_breweries.extend(data)
            page += 1
        response.raise_for_status()
        logger.info(f"{len(all_breweries)} registros carregados da API.")
        return all_breweries
    except requests.RequestException as e:
        logger.error(f"Erro ao conectar com a API: {e}")
        raise


def process_brewery_data(execution_date=None):
    config = load_config()

    spark = create_spark_session()

    logger.info("SparkSession iniciada.")

    source_path = config["source"]["path"]

    sink_path = config["sink"]["path"]
    format_ = config["sink"]["format"]

    # Tentar ler dados existentes do S3
    try:
        logger.info(f"Tentando ler dados existentes de {source_path}")
        existing_df = spark.read.json(source_path)
        logger.info(f"Encontrados {existing_df.count()} registros existentes.")
        bucket_empty = False
    except Exception as e:
        logger.warning(
            f"Nenhum dado existente encontrado. Bucket vazio. Detalhe: {e}"
        )
        bucket_empty = True

    # Buscar dados da API
    breweries = fetch_brewery_from_api()

    # Criar DataFrame novo
    new_df = spark.read.json(
        spark.sparkContext.parallelize(
            [json.dumps(record) for record in breweries]
        )
    )

    if isinstance(execution_date, str):
        execution_date_str = execution_date
    else:
        execution_date_str = execution_date.strftime("%Y-%m-%d")

    # Adicionar a coluna "ds" com a data de execução
    new_df = new_df.withColumn("date_execution", lit(execution_date_str))

    if bucket_empty:
        # Primeira carga
        logger.info("Bucket vazio. Realizando primeira carga completa.")
        save_data(new_df, sink_path, format_)
        spark.stop()
        return True
    else:
        # Comparar IDs
        logger.info("Comparando registros novos com existentes.")
        existing_ids = [
            row["id"] for row in existing_df.select("id").collect()
        ]
        logger.info(f"IDs existentes carregados: {len(existing_ids)}")
        filtered_df = new_df.filter(~col("id").isin(existing_ids))
        if filtered_df.count() == 0:
            logger.info("Nenhum novo registro encontrado. Finalizando.")
            spark.stop()
            return False

        logger.info(
            f"Novos registros encontrados: {filtered_df.count()}. Salvando..."
        )
        save_data(filtered_df, sink_path, format_)
        return True
        spark.stop()


def save_data(df, path, format_):
    logger.info(f"Salvando dados em {path} como {format_}...")
    df.write.mode("append").format(format_).save(path)
    logger.info("Dados salvos com sucesso.")


if __name__ == "__main__":
    process_brewery_data()
