"""
Basic Airflow DAG Example
------------------------
This script demonstrates a basic Airflow DAG (Directed Acyclic Graph)
with simple tasks and dependencies.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': days_ago(1),
}

# Create the DAG
dag = DAG(
    'basic_workflow_example',
    default_args=default_args,
    description='A basic workflow example',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['example', 'basic'],
)

# Define Python functions for tasks
def print_context(**kwargs):
    """Print the Airflow context and ds variable from the context."""
    print(kwargs)
    print(f"Execution date: {kwargs['ds']}")
    return 'Context printed successfully!'

def process_data(**kwargs):
    """Simulate data processing."""
    print("Processing data...")
    # Simulate some data processing
    data = {'value1': 100, 'value2': 200, 'value3': 300}
    # Pass data to the next task using XCom
    kwargs['ti'].xcom_push(key='processed_data', value=data)
    return 'Data processed successfully!'

def analyze_data(**kwargs):
    """Analyze data from the previous task."""
    ti = kwargs['ti']
    # Get data from the previous task using XCom
    data = ti.xcom_pull(task_ids='process_data', key='processed_data')
    print(f"Analyzing data: {data}")
    # Perform some analysis
    total = sum(data.values())
    average = total / len(data)
    result = {'total': total, 'average': average}
    # Pass results to the next task
    ti.xcom_push(key='analysis_result', value=result)
    return 'Data analyzed successfully!'

def generate_report(**kwargs):
    """Generate a report from the analysis results."""
    ti = kwargs['ti']
    # Get analysis results from the previous task
    results = ti.xcom_pull(task_ids='analyze_data', key='analysis_result')
    print(f"Generating report with results: {results}")
    # Generate a simple report
    report = f"""
    Data Analysis Report
    -------------------
    Date: {kwargs['ds']}
    Total: {results['total']}
    Average: {results['average']}
    """
    # Save the report to a file
    with open('/tmp/report.txt', 'w') as f:
        f.write(report)
    return 'Report generated successfully!'

# Create tasks using operators
start_task = BashOperator(
    task_id='start_workflow',
    bash_command='echo "Starting workflow at $(date)"',
    dag=dag,
)

print_context_task = PythonOperator(
    task_id='print_context',
    python_callable=print_context,
    provide_context=True,
    dag=dag,
)

process_data_task = PythonOperator(
    task_id='process_data',
    python_callable=process_data,
    provide_context=True,
    dag=dag,
)

analyze_data_task = PythonOperator(
    task_id='analyze_data',
    python_callable=analyze_data,
    provide_context=True,
    dag=dag,
)

generate_report_task = PythonOperator(
    task_id='generate_report',
    python_callable=generate_report,
    provide_context=True,
    dag=dag,
)

end_task = BashOperator(
    task_id='end_workflow',
    bash_command='echo "Workflow completed at $(date)"',
    dag=dag,
)

# Define task dependencies
start_task >> print_context_task >> process_data_task >> analyze_data_task >> generate_report_task >> end_task
