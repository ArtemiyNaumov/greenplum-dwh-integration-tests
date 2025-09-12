from pathlib import Path
from typing import Dict, List
import os

from gp_dwh_integration_tests.app import app

query = """select column_name, data_type
            from information_schema.columns
            where table_schema = '{schema}'
            and table_name = '{table}';"""


error_msg1 = """В таблице {}.{} на dev не хватает полей {}"""
error_msg2 = """В таблице {}.{} на dev есть лишние поля {}"""
error_msg3 = """В таблице {}.{} не сходятся типы полей {}"""

@app.check(
    id='D002',
    depends_on=[],
    label='tables',
    ignore=[],
    processing = ['dev'],
    level = 'WARNING'
)
def check_table_attributes(conn, dp_schema, dp_object, dev_conn) -> None:
    '''
    Checks attributes of a table
    '''
    local_res = conn.execute_sql_query(query, schema=dp_schema, table=dp_object)

    dev_res = dev_conn.execute_sql_query(query, schema=dp_schema, table=dp_object)

    if len(local_res) > 0 and len(dev_res) > 0:
        dict_local = dict(local_res)
        dict_dev = dict(dev_res)

        atts_only_in_local = set(dict_local.keys()) - set(dict_dev.keys())
        atts_only_in_dev = set(dict_dev.keys()) - set(dict_local.keys())

        atts_with_different_types = {
            key for key in dict_dev.keys() & dict_local.keys() if dict_dev[key] != dict_local[key]
        }

        assert len(list(atts_only_in_local)) == 0, error_msg1.format(dp_schema, dp_object, str(atts_only_in_local))
        assert len(list(atts_only_in_dev)) == 0, error_msg2.format(dp_schema, dp_object, str(atts_only_in_dev)) 
        assert len(list(atts_with_different_types)) == 0, error_msg3.format(dp_schema, dp_object, str(atts_with_different_types))
