get_all_functions= """select p.proname || '(' || oidvectortypes(p.proargtypes) || ')'
                      from pg_proc p inner join pg_namespace ns on (p.pronamespace = ns.oid)
                      where ns.nspname = '{schema}';"""

get_all_tables = """select t.tablename
                    from pg_tables t
                    left join pg_partitions p1
                        on t.tablename = p1.tablename and p1.partitionisdefault = true
                    left join pg_partitions p2
                        on t.tablename = p2.partitiontablename and p2.partitionisdefault = true
                    where t.schemaname = '{schema}'
                    and p2.tablename is null
                    and not (t.tablename like '%_prt_%');
"""

get_all_views = """select table_name
                    from information_schema."tables"
                    where table_schema = '{schema}'
                    and table_type = 'VIEW';"""

get_processing_type = """select obj_description(ns.oid, 'pg_namespace')
                        from pg_namespace ns
                        where nspname = '{schema}';"""
