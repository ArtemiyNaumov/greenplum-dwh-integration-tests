from pathlib import Path
from typing import Dict, List
import os

from gp_dwh_integration_tests.app import app

query = """ select c.column_name
            from information_schema.columns c
            where column_default is not null
            and c.table_schema  = '{schema}' 
                and c.table_name = '{table}';"""


error_msg = """Таблица {}.{} 
Default значения допускаются только в полях аудита 'created_dttm', 'updated_dttm', 'deleted_dttm'
Надо убрать default из поля {}"""

@app.check(
    id='T010',
    depends_on=[],
    label='tables',
    ignore=['schemachangelog', 'schemachangeloglock'],
    level='WARNING',
    processing = ['DP2.0', 'marts', 'P3']
)
def check_default_values(conn, dp_schema, dp_object, dev_conn) -> None:
    '''
    Checks if tables do not have default values
    '''

    audit_columns = ['created_dttm', 
                     'updated_dttm', 
                     'deleted_dttm']

    res = conn.execute_sql_query(query, schema=dp_schema, table=dp_object)
    if len(res) > 0:
        for elem in res:
            assert elem[0] in audit_columns, error_msg.format(dp_schema, dp_object, elem[0])
