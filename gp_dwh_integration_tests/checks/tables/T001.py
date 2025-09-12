from pathlib import Path
from typing import Dict, List
import os

from gp_dwh_integration_tests.app import app

query = """select c.reloptions
           from pg_class as c
           inner join pg_namespace as n
            on c.relnamespace = n.oid
           where
            n.nspname = '{schema}'
            and c.relname = '{table}'
            and c.relname not in ('schemachangelog', 'schemachangeloglock');"""

error_msg = """Таблицы в слоях ODS и marts должны быть колоночно-ориентированными.
Проверьте параметры хранения для таблицы {}.{}.
Корректные параметры хранения: 
'appendonly=true', 'compresslevel=1', 'orientation=column', 'compresstype=zstd'
"""

@app.check(
    id='T001',
    depends_on=[],
    label='tables',
    ignore=['schemachangelog', 'schemachangeloglock'],
    processing = ['DP2.0', 'marts', 'P3'],
    level = 'WARNING'
)
def check_storage_parameters(conn, dp_schema, dp_object, dev_conn) -> None:
    '''
    Checks storage parameters for the table are set correctly
    '''

    params = {'appendonly': 'true',
              'compresslevel': '1',
              'orientation': 'column',
              'compresstype': 'zstd'}

    res = conn.execute_sql_query(query, schema=dp_schema, table=dp_object)[0][0]

    assert not(res is None),  error_msg.format(dp_schema, dp_object)
    
    received_parameters = {}
    for param in res:
        key, value = param.split('=')
        received_parameters[key] = value

    for key in params:
        assert key in received_parameters, 'Свойство {} не задано для {}'.format(key, 
                                                                     dp_object)
        
        assert received_parameters[key] == params[key], error_msg.format(dp_schema, 
                                                                         dp_object)