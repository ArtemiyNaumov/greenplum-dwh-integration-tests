from pathlib import Path
from typing import Dict, List
import os

from gp_dwh_integration_tests.app import app

query = """ select column_name,
            case 
                when domain_name is not null then domain_name
                when data_type='character varying' THEN 'varchar('||character_maximum_length||')'
                when data_type='numeric' THEN 'numeric('||numeric_precision||','||numeric_scale||')'
                when data_type='character' THEN 'character('||character_maximum_length||')'
                else data_type
            end as myType
            from information_schema.columns
            where table_schema = '{schema}'
                and table_name='{table}';"""


error_msg1 = """Атрибут {} обязателен для интеграции по Processing 1.0. 
Его необходимо добавить в таблицу {}.{}.
"""

error_msg2 = """Тип данных атрибута {}.{}.{} должен быть {}.
"""

tech_cols_ods = {'nk': 'varchar(4096)',
                'valid_from_dttm':	'timestamp without time zone',
                'created_dttm': 'timestamp without time zone',
                'updated_dttm': 'timestamp without time zone',
                'md5_hash': 'varchar(4096)',
                'is_actual': 'character(1)'}

tech_cols_ods_hist = {'nk': 'varchar(4096)',
                    'valid_from_dttm': 'timestamp without time zone',
                    'valid_to_dttm': 'timestamp without time zone',
                    'created_dttm': 'timestamp without time zone',
                    'updated_dttm': 'timestamp without time zone',
                    'deleted_dttm': 'timestamp without time zone',
                    'md5_hash': 'varchar(4096)',
                    'is_actual': 'character(1)'}

tech_cols_raw_h = {'dt_created': 'timestamp without time zone',
                   'is_init': 'boolean',
                    'h': 'USER-DEFINED'}

tech_cols_raw_tmp = {'nk': 'text',
                     'op_type': 'character(1)',
                     'op_ts': 'timestamp without time zone',
                     'pos': 'varchar(256)',
                     'dt_created': 'timestamp without time zone',
                     'is_init': 'character(1)',
                     'h': 'USER-DEFINED'}

@app.check(
    id='V003',
    depends_on=[],
    label='views',
    ignore=[],
    level='WARNING',
    processing = ['P1']
)
def check_p1_vw_attributes(conn, dp_schema, dp_object, dev_conn) -> None:
    '''
    Mandatory attributes for P1 integration
    '''

    if dp_schema.endswith('_raw') and dp_object.startswith('h_'):
        col_dict = tech_cols_raw_h
    elif dp_schema.endswith('_raw') and dp_object.startswith('tmp_'):
        col_dict = tech_cols_raw_tmp
    elif dp_schema.endswith('_ods') and dp_object.endswith('_hist'):
        col_dict = tech_cols_ods_hist
    elif dp_schema.endswith('_ods') and not(dp_object.endswith('_hist')):
        col_dict = tech_cols_ods
    else:
        assert 1==1

    res = conn.execute_sql_query(query, schema=dp_schema, table=dp_object)

    res_dict = {elem[0]: elem[1] for elem in res}

    for col in col_dict:
        assert col in res_dict, error_msg1.format(col,
                                                  dp_schema,
                                                  dp_object)

        assert col_dict[col] == res_dict[col], error_msg2.format(dp_schema,
                                                                dp_object,
                                                                col_dict[col])
