from pathlib import Path
from typing import Dict, List
import os

from gp_dwh_integration_tests.app import app

query = """ select vc.column_name
            from information_schema.view_table_usage u
            join information_schema.columns vc on u.view_schema = vc.table_schema
                and u.view_name = vc.table_name 
            left join information_schema.columns tc on u.table_schema = tc.table_schema
                and u.table_name = tc.table_name
                and vc.column_name = tc.column_name
            where view_schema = '{schema}'
                and view_name='{table}'
                and tc.column_name is null;"""



error_msg = """Представления в слоях ods и marts должны соответствовать таблицам.
Проверьте, что поле {} существует в таблице, на которую ссылается представление {}.{}.
"""


@app.check(
    id='V002',
    depends_on=[],
    label='views',
    ignore=[],
    processing = ['DP2.0', 'marts', 'P3'],
    level = 'WARNING'
)
def check_column_conformity(conn, dp_schema, dp_object, dev_conn) -> None:
    '''
    Check if view represents table
    '''

    res = conn.execute_sql_query(query, schema=dp_schema, table=dp_object)

    assert len(res) == 0, error_msg.format(res, dp_schema, dp_object)
