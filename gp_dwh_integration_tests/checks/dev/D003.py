from pathlib import Path
from typing import Dict, List
import os

from gp_dwh_integration_tests.app import app

query = """select viewname, viewowner 
            from pg_catalog.pg_views
            where viewname = '{table}'
            and schemaname = '{schema}';"""


error_msg1 = """Представление {}.{} уже существует на dev"""
error_msg2 = """Представление {}.{} должно уже существовать на dev"""
error_msg3 = """Владелец представления {}.{} на dev-контуре {}, а должен быть {}"""

@app.check(
    id='D003',
    depends_on=[],
    label='views',
    ignore=[],
    processing = ['dev'],
    level = 'WARNING'
)
def check_view_owners(conn, dp_schema, dp_object, dev_conn) -> None:
    '''
    Checks table existence in both environments and it's owners
    '''
    local_res = conn.execute_sql_query(query, schema=dp_schema, table=dp_object)

    dev_res = dev_conn.execute_sql_query(query, schema=dp_schema, table=dp_object)
    
    if len(local_res) == 0 and len(dev_res) > 0:
        assert 1==0, error_msg1.format(dp_schema, dp_object)
    if len(local_res) > 0 and len(dev_res) == 0:
        assert 1==0, error_msg2.format(dp_schema, dp_object)
    if len(local_res) == 1 and len(dev_res) == 1 and local_res[0][1] != dev_res[0][1]:
        assert 1==0, error_msg3.format(dp_schema, dp_object, dev_res[0][1], local_res[0][1])
