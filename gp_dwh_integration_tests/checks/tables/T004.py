from pathlib import Path
from typing import Dict, List
import os

from gp_dwh_integration_tests.app import app

query = """ select ts.spcname
            from pg_class c
            left join pg_tablespace ts on c.reltablespace = ts.oid
            join pg_namespace as n
            on c.relnamespace = n.oid
            where
            n.nspname = '{schema}'
            and c.relname = '{table}';
            """


error_msg = """По возможности, таблицы надо создавать в табличном пространстве WARM.
Рассмотрите возможность переноса на WARM таблицы {}.{}.
"""

@app.check(
    id='T004',
    depends_on=[],
    label='tables',
    ignore=['schemachangelog', 'schemachangeloglock'],
    processing = ['DP2.0', 'marts', 'P1', 'P3'],
    level = 'WARNING'
)
def check_tablespace(conn, dp_schema, dp_object, dev_conn) -> None:
    '''
    Check if table is in tablespace warm
    '''

    res = conn.execute_sql_query(query, schema=dp_schema, table=dp_object)[0][0]

    assert res == 'warm', error_msg.format(dp_schema, dp_object)
