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


error_msg1 = """Поле {} обязательно для интеграции по процессингу DP2.0.
Его необходимо добавить в таблицу {}.{}.
"""

error_msg2 = """Тип данных поля {}.{}.{} должен быть {}.
"""

tech_cols = {'nk': 'varchar(4096)',
                'valid_from_dttm':	'timestamp with time zone',
                'created_dttm': 'timestamp without time zone',
                'updated_dttm': 'timestamp without time zone',
                'md5_hash': 'varchar(4096)',
                'is_actual': 'character(1)'}

tech_cols_hist = {'nk': 'varchar(4096)',
                    'valid_from_dttm': 'timestamp with time zone',
                    'valid_to_dttm': 'timestamp with time zone',
                    'created_dttm': 'timestamp without time zone',
                    'updated_dttm': 'timestamp without time zone',
                    'deleted_dttm': 'timestamp without time zone',
                    'md5_hash': 'varchar(4096)',
                    'is_actual': 'character(1)'}


@app.check(
    id='T003',
    depends_on=[],
    label='tables',
    ignore=['schemachangelog', 'schemachangeloglock'],
    level='WARNING',
    processing = ['DP2.0']
)
def check_dp2_attributes(conn, dp_schema, dp_object, dev_conn) -> None:
    '''
    Mandatory attributes for DP2.0 integration
    '''

    col_dict = tech_cols_hist if dp_object.endswith('_hist') else tech_cols

    res = conn.execute_sql_query(query, schema=dp_schema, table=dp_object)

    res_dict = {elem[0]: elem[1] for elem in res}

    for col in col_dict:
        assert col in res_dict, error_msg1.format(col,
                                                  dp_schema,
                                                  dp_object)

        assert col_dict[col] == res_dict[col], error_msg2.format(dp_schema,
                                                                dp_object,
                                                                col,
                                                                col_dict[col])
