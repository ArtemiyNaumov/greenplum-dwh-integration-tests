from pathlib import Path
from typing import Dict, List

from gp_dwh_integration_tests.app import app

query = """select count(*)
            from pg_roles er 
            where rolname 
            in ('{schema}_w',
                '{schema}_r',
                '{schema}_x',
                '{schema}_rw',
                '{schema}_rwx');"""

error_msg = """Default roles:
'{schema}_w',
'{schema}_r',
'{schema}_x',
'{schema}_rw',
'{schema}_rwx
должны быть созданы в файле init.sql'"""

@app.check(
    id='C002',
    depends_on=[],
    label='common',
    level='WARNING',
    processing = ['DP2.0', 'marts', 'P3']
)
def check_default_roles(conn, dp_schema, dp_object, dev_conn) -> None:
    '''
    Checks if default roles are created
    '''
    res = conn.execute_sql_query(query, schema=dp_schema)[0][0]
    assert res == 5, error_msg.format(schema=dp_schema)