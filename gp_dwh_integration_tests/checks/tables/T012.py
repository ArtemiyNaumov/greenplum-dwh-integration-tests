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
        and column_name !~ '^[a-zA-Z0-9_]+$';
"""

error_msg = """Таблица {}.{}
В названиях колонок запрещено использование букв не латинского алфавита
и специальных символов, кроме `_`.\nНеобходимо переименовать поля: {}
"""

@app.check(
    id='T012',
    depends_on=[],
    label='tables',
    ignore=['schemachangelog', 'schemachangeloglock'],
    level='WARNING',
    processing = ['DP2.0', 'marts', 'P3']
)
def check_not_null_constraints(conn, dp_schema, dp_object, dev_conn) -> None:
    '''
    Checks if tables columns' names do not contain
    non-latin and non-numeric characters
    '''

    res = conn.execute_sql_query(query, schema=dp_schema, table=dp_object)
    if len(res) > 0:
        error_columns = [elem[0] for elem in res]
        assert False, error_msg.format(dp_schema, dp_object, ', '.join(error_columns))
