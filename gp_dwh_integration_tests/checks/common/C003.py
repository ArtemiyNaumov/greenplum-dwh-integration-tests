from pathlib import Path
from typing import Dict, List
import os

from gp_dwh_integration_tests.app import app


query = """SELECT count(*)
           FROM pg_roles r1
           join pg_roles r2 on pg_has_role(r2.rolname, r1.oid, 'member')
           WHERE r2.rolname like '%_etlbot'
	        and r1.rolname = '{schema}_rwx';"""

@app.check(
    id='C003',
    depends_on=[],
    label='common',
    level='WARNING',
    processing = ['DP2.0', 'marts', 'P3']
)
def check_etlbot_grant(conn, dp_schema, dp_object, dev_conn) -> None:
    '''
    Checks if rwx is granted to a etlbot
    '''
    res = conn.execute_sql_query(query, schema=dp_schema)[0][0]
    
    assert res > 0, 'Роль {}_rwx должна быть выдана хотя бы одному etlbot'.format(dp_schema)
