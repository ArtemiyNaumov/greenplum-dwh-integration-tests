from pathlib import Path
from typing import Dict, List
import os

from gp_dwh_integration_tests.app import app

query = """ select count(*)
            from information_schema.view_table_usage u
            where table_schema = '{schema}'
                and table_name='{table}';
            """


error_msg = """Таблица {}.{} не используется ни одним представлением.
Если так и задумано, добавьте эту таблицу в игнор (файл dwh-integration-tests.yml в dwh-db).
"""

@app.check(
    id='T005',
    depends_on=[],
    label='tables',
    ignore=['schemachangelog', 'schemachangeloglock'],
    processing = ['DP2.0', 'marts', 'P3'],
    level = 'WARNING'
)
def check_table_usage(conn, dp_schema, dp_object, dev_conn) -> None:
    '''
    Check if table is used by at least one view
    '''

    res = conn.execute_sql_query(query, schema=dp_schema, table=dp_object)[0][0]

    assert res > 0, error_msg.format(dp_schema, dp_object)