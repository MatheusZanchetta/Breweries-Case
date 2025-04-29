from breweries_case.analytics.job import AnalyticsdBrewryData
from breweries_case.curated.job import CuratedBrewryData
from breweries_case.raw.job import process_brewery_data
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

from airflow.operators.python import ShortCircuitOperator

# Ajustar o path para importar o job
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Importa a função principal do job

# Configurações padrão da DAG
default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 4, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

# Criação da DAG
with DAG(
    dag_id="brewery_case",
    default_args=default_args,
    description="Pipeline - Breweries",
    schedule_interval="0 12 * * *",
    catchup=False,
    tags=["raw", "brewery"],
) as dag:
    dag.doc_md = __doc__

    def data_flow():
        verify_new_data = ShortCircuitOperator(
            task_id="check_new_data",
            python_callable=process_brewery_data,
            op_kwargs={"execution_date": "{{ ds }}"},
        )
        curated_task = PythonOperator(
            task_id="curated_data",
            python_callable=CuratedBrewryData,
            op_kwargs={"execution_date": "{{ ds }}"},
        )
        analytics_task = PythonOperator(
            task_id="analytics_data",
            python_callable=AnalyticsdBrewryData,
            op_kwargs={"execution_date": "{{ ds }}"},
        )
        verify_new_data >> curated_task >> analytics_task

    data_flow()
