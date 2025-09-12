from pathlib import Path
from typing import Dict, List
import os

from gp_dwh_integration_tests.app import app


query_vw = """ select tab1.table_name 
            from information_schema."tables" tab1 
            left join information_schema.role_table_grants tg
                on tg.table_name = tab1.table_name
                and (tg.grantee = '{schema}_r')
            where tab1.table_schema  = '{schema}'
            and tab1.table_type = 'VIEW'
            and tg.table_name is null;
"""

error_msg_vw = """Не выдан доступ на чтение следующих представлений: {}"""

query_tab = """ select distinct tab1.tablename
                from pg_tables tab1 
                left join information_schema.role_table_grants tg
                    on tg.table_name = tab1.tablename
                    and tg.grantee = '{schema}_w'
                where tab1.schemaname  = '{schema}'
                and tg.table_name is null
                and tab1.tablename not in ('schemachangeloglock',
                                        'schemachangelog');

"""

error_msg_tab = """Не выдан доступ на запись в следующие таблицы: {}"""

query_fun = """ select p.proname 
                FROM pg_catalog.pg_proc p
                JOIN pg_catalog.pg_namespace n ON n.oid = p.pronamespace
                left join information_schema.routine_privileges g
                    on g.routine_name = p.proname 
                    and g.grantee = '{schema}_x'
                where n.nspname = '{schema}'
                    and g.routine_name is null;
"""

error_msg_fun = """Не выдан доступ на выполнение следующих функций: {}"""


@app.check(
    id='C005',
    depends_on=[],
    label='common',
    level='WARNING',
    processing = ['DP2.0', 'marts', 'P3']
)
def check_default_grants(conn, dp_schema, dp_object, dev_conn) -> None:
    '''
    Checks if default roles are granted properly
    '''
    res_vw = [elem[0] for elem in conn.execute_sql_query(query_vw, schema=dp_schema)]
    assert len(res_vw) == 0, error_msg_vw.format(res_vw)

    res_tab = [elem[0] for elem in conn.execute_sql_query(query_tab, schema=dp_schema)]
    assert len(res_tab) == 0, error_msg_tab.format(res_tab)

    res_fun = [elem[0] for elem in conn.execute_sql_query(query_fun, schema=dp_schema)]
    assert len(res_fun) == 0, error_msg_fun.format(res_fun)
