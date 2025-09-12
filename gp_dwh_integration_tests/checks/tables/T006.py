from pathlib import Path
from typing import Dict, List
import os

from gp_dwh_integration_tests.app import app

query = """ select count(*)
            from pg_tables t
            left join pg_partitions p1
                on t.tablename = p1.tablename and p1.partitionisdefault = true
            left join pg_partitions p2
                on t.tablename = p2.partitiontablename and p2.partitionisdefault = true
            where t.schemaname = '{schema}'
                and t.tablename = '{table}'
                and p1.tablename is null
                and p2.tablename is null;
            """

error_msg = """Таблица {}.{} не партиционирована. 
Для добавления дефолтной партиции просьба воспользоваться инструкцией
"""

@app.check(
    id='T006',
    depends_on=[],
    label='tables',
    ignore=['schemachangelog', 'schemachangeloglock'],
    processing = ['DP2.0', 'marts', 'P3'],
    level = 'WARNING'
)
def check_table_partitioning(conn, dp_schema, dp_object, dev_conn) -> None:
    '''
    Check if table is partitioned
    '''

    res = conn.execute_sql_query(query, schema=dp_schema, table=dp_object)[0][0]

    assert res == 0, error_msg.format(dp_schema, dp_object)