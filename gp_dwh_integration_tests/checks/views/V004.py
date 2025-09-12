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


error_msg1 = """Атрибут {} обязателен для интеграции по Processing 3.0.
Его необходимо добавить в таблицу {}.{}.
"""

error_msg2 = """Тип данных атрибута {}.{}.{} должен быть {}.
"""

tech_cols_ods = {'business_dt': 'date'}

@app.check(
    id='V004',
    depends_on=[],
    label='views',
    ignore=[],
    level='WARNING',
    processing = ['P3']
)
def check_p3_vw_attributes(conn, dp_schema, dp_object, dev_conn) -> None:
    '''
    Mandatory attributes for P3 integration
    '''

    col_dict = tech_cols_ods

    res = conn.execute_sql_query(query, schema=dp_schema, table=dp_object)

    res_dict = {elem[0]: elem[1] for elem in res}

    for col in col_dict:
        assert col in res_dict, error_msg1.format(col,
                                                  dp_schema,
                                                  dp_object)

        assert col_dict[col] == res_dict[col], error_msg2.format(dp_schema,
                                                                dp_object,
                                                                col_dict[col])
