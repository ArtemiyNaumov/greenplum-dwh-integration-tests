from pathlib import Path
from typing import Dict, List
import os

from gp_dwh_integration_tests.app import app

query = """select pgp.proname || '(' || oidvectortypes(pgp.proargtypes) || ')', pgr.rolname 
            from pg_catalog.pg_proc pgp
            join pg_catalog.pg_namespace pgn on pgn.oid = pgp.pronamespace 
            join pg_catalog.pg_roles pgr on pgr.oid = pgp.proowner
            where pgn.nspname = '{schema}'
            and pgp.proname = '{func}';"""


error_msg1 = """Функция {}.{} уже существует на dev"""
error_msg2 = """Функция {}.{} должна уже существовать на dev"""
error_msg3 = """Владелец функции {}.{} на dev-контуре {}, а должен быть {}"""

@app.check(
    id='D005',
    depends_on=[],
    label='functions',
    ignore=[],
    processing = ['dev'],
    level = 'WARNING'
)
def check_function_owners(conn, dp_schema, dp_object, dev_conn) -> None:
    '''
    Checks function existence in both environments and it's owners
    '''
    local_res = conn.execute_sql_query(query, schema=dp_schema, func=dp_object)

    dev_res = dev_conn.execute_sql_query(query, schema=dp_schema, func=dp_object)
    
    if len(local_res) == 0 and len(dev_res) > 0:
        assert 1==0, error_msg1.format(dp_schema, dp_object)
    if len(local_res) > 0 and len(dev_res) == 0:
        assert 1==0, error_msg2.format(dp_schema, dp_object)
    if len(local_res) == 1 and len(dev_res) == 1 and local_res[0][1] != dev_res[0][1]:
        assert 1==0, error_msg3.format(dp_schema, dp_object, dev_res[0][1], local_res[0][1])
