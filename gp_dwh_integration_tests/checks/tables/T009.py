from pathlib import Path
from typing import Dict, List
import os

from gp_dwh_integration_tests.app import app

query = """ SELECT c.data_type
            FROM pg_partition_columns p
            join information_schema.columns c on p.schemaname = c.table_schema 
                and p.tablename = c.table_name 
                and p.columnname = c.column_name 
            join pg_catalog.pg_class cl on cl.relname = c.table_name 
            join pg_catalog.pg_namespace n on n.oid = cl.relnamespace and n.nspname = c.table_schema 
            join pg_catalog.pg_partition pp on cl.oid = pp.parrelid and pp.parkind = 'r'
            where c.table_schema  = '{schema}' 
                and c.table_name = '{table}';"""


error_msg = """Таблица {}.{} 
Поле партиционирования может быть только типа timestamp или date."""

@app.check(
    id='T009',
    depends_on=[],
    label='tables',
    ignore=['schemachangelog', 'schemachangeloglock'],
    level='WARNING',
    processing = ['DP2.0', 'marts', 'P3', 'P1']
)
def check_partitioning_column_type(conn, dp_schema, dp_object, dev_conn) -> None:
    '''
    Checks if type of the partitioning column is either timestamp or date
    '''

    supported_types = ['timestamp with time zone',
                       'timestamp without time zone',
                       'date']

    res = conn.execute_sql_query(query, schema=dp_schema, table=dp_object)
    if len(res) > 0 and len(res[0]) == 1:
        assert res[0][0] in supported_types, error_msg.format(dp_schema, dp_object)
