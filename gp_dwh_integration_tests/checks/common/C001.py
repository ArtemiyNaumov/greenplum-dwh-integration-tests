from pathlib import Path
from typing import Dict, List
import os

from gp_dwh_integration_tests.app import app


query = """select count(*)
           from pg_catalog.pg_namespace 
           where nspname = '{schema}';"""

@app.check(
    id='C001',
    depends_on=[],
    label='common',
    level='WARNING',
    processing = ['DP2.0', 'marts', 'P1', 'P3']
)
def check_schema_creation(conn, dp_schema, dp_object, dev_conn) -> None:
    '''
    Checks if schema has been created
    '''
    res = conn.execute_sql_query(query, schema=dp_schema)[0][0]
    
    assert res == 1, 'Схема {} не была создана'.format(dp_schema)
