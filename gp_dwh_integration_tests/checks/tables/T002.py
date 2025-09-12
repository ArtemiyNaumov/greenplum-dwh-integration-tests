from pathlib import Path
from typing import Dict, List
import os

from gp_dwh_integration_tests.app import app

query = """ select pga.attname, pgae.attoptions
            from pg_attribute pga
            join pg_attribute_encoding pgae
            on pga.attrelid = pgae.attrelid and pga.attnum = pgae.attnum 
            join pg_class pgc on pgc.oid = pga.attrelid
            join pg_namespace pgn on pgn.oid = pgc.relnamespace 
            where nspname = '{schema}'
                and relname = '{table}'
                and pga.atttypid <> 0;"""

error_msg = """Таблицы в слоях ODS и marts должны быть колоночно-ориентированными.
Проверьте параметры хранения для атрибута {}.{}.{}.
Корректные параметры:
'blocksize': '32768', 'compresslevel=1', 'compresstype=zstd'.
Если поле атрибут был добавлен ранее с неправильными параметрами хранения (к примеру, не был указан ENCODING), таблицу необходимо пересоздать.  
"""

@app.check(
    id='T002',
    depends_on=[],
    label='tables',
    ignore=['schemachangelog', 'schemachangeloglock'],
    processing = ['DP2.0', 'marts', 'P3'],
    level = 'WARNING'
)
def check_attribute_storage(conn, dp_schema, dp_object, dev_conn) -> None:
    '''
    Checks storage parameters for each attribute
    '''

    params = {'compresslevel': '1',
              'blocksize': '32768',
              'compresstype': 'zstd'}


    res = conn.execute_sql_query(query, schema=dp_schema, table=dp_object)

    for col in res:
        received_parameters = {}
        for param in col[1]:
            key, value = param.split('=')
            received_parameters[key] = value

        for key in received_parameters:
            assert key in params, 'Property {} is not set for {}.{}'.format(key, 
                                                                        dp_object,
                                                                        col[0])
            
            assert received_parameters[key] == params[key], error_msg.format(dp_schema, 
                                                                            dp_object,
                                                                            col[0])