from pathlib import Path
from typing import Dict, List
import os

from gp_dwh_integration_tests.app import app

query = """ 
    select
        column_name 
    from information_schema.columns 
    where
        table_schema = '{schema}' 
        and table_name = '{table}'
        and is_nullable = 'NO';
"""

error_msg = """Таблица {}.{}
Рекомендуется не использовать ограничение целостности `NOT NULL`
в любых слоях данных.\nНеобходимо убрать `NOT NULL` для полей: {}
"""

@app.check(
    id='T011',
    depends_on=[],
    label='tables',
    ignore=['schemachangelog', 'schemachangeloglock'],
    level='WARNING',
    processing = ['DP2.0', 'marts', 'P3']
)
def check_not_null_constraints(conn, dp_schema, dp_object, dev_conn) -> None:
    '''
    Checks if tables' columns do not have `NOT NULL` constraints
    '''

    audit_columns = ['created_dttm', 
                     'updated_dttm', 
                     'deleted_dttm']
    
    res = conn.execute_sql_query(query, schema=dp_schema, table=dp_object)
    if len(res) > 0:
        error_columns = [elem[0] for elem in res if elem[0] not in audit_columns]
        if len(error_columns) > 0:
            assert False, error_msg.format(dp_schema, dp_object, ', '.join(error_columns))
