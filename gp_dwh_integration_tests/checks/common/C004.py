from pathlib import Path
from typing import Dict, List
import os

from gp_dwh_integration_tests.app import app


query = """SELECT count(*)
           FROM  pg_roles r1
           join pg_roles r2 on pg_has_role(r2.rolname, r1.oid, 'member')
           join pg_roles r3 on pg_has_role(r2.rolname, r3.oid, 'member')
           WHERE r2.rolname like '%_etlbot'
	        and r1.rolname = '{schema}_rwx'
	        and r3.rolname = 'pxf_select';"""


@app.check(
    id='C004',
    depends_on=[],
    label='common',
    level='WARNING',
    processing = ['DP2.0', 'P3']
)
def check_pxf_select(conn, dp_schema, dp_object, dev_conn) -> None:
    '''
    Checks if pxf_select is granted in DP2.0 integration
    '''
    res = conn.execute_sql_query(query, schema=dp_schema)[0][0]
        
    assert res > 0, 'pxf_select должен быть выдан etlbot'.format(dp_schema)
