from enum import Enum
from pathlib import Path
from typing import Callable, Dict, List, Optional
import psycopg2
import os

import chardet

from pydantic import BaseModel, validator

from gp_dwh_integration_tests.config import SQL_PATH

from gp_dwh_integration_tests.registrator.exceptions import (
    GetProcessingError
)

from gp_dwh_integration_tests.query import (
    get_all_functions,
    get_all_tables,
    get_all_views,
    get_processing_type
)

class CheckLevel(str, Enum):
    WARNING: str = 'WARNING'
    FAILURE: str = 'FAILURE'


STATUS_MAPPING: Dict[CheckLevel, str] = {
    CheckLevel.WARNING: 2,
    CheckLevel.FAILURE: 1
}


class CheckResult(BaseModel):
    '''Class for keeping check result'''
    id: str = ...
    status: int = 0
    exception: Optional[str] = None


class Check(BaseModel):
    '''Class for keeping check description'''
    id: str = ...
    description: Optional[str] = None
    dp_schema: Optional[str] = None
    sql_path: Optional[str] = None
    ignore: Optional[List[str]] = None
    level: CheckLevel = CheckLevel.FAILURE
    callable: Callable = ...
    depends_on: Optional[List[str]] = None
    label: Optional[str] = None
    processing: Optional[List[str]] = None


    @validator('description', pre=True)
    def strip_description(cls, description):  # noqa: N805
        if description is not None:
            return description.strip()

        return description

    def apply(self, conn, dp_schema, dp_object, dev_conn=None) -> CheckResult:
        '''
        Applies check
        '''

        status = 0
        result = {
            'id': self.id,
            'status': status
        }

        try:
            self.callable(conn, dp_schema, dp_object, dev_conn)
        except AssertionError as ex:
            status = STATUS_MAPPING[self.level]
            result.update({'status': status, 'exception': str(ex)})
        except Exception as ex:
            status = 3
            result.update({'status': status, 'exception': str(ex)})

        return CheckResult(**result)
    
class Connection:
    def __init__(self, gp_schema=None, **kwargs):
        self.gp_schema = gp_schema
        self.conn = self.get_gp_conn(**kwargs)

    def get_gp_conn(self, **kwargs):
        db_host = kwargs.get('db_host')or os.getenv('DB_HOST') or 'localhost'
        db_port = kwargs.get('db_port') or 5432
        db_name = kwargs.get('db_name') or 'adb'
        db_user = kwargs.get('db_user') or os.getenv('DB_USER')
        db_pwd = kwargs.get('db_pwd') or os.getenv('DB_PWD')

        return psycopg2.connect("dbname='{}' user='{}' host='{}'" \
                                "port='{}' password='{}'".format(db_name, db_user,
                                                                db_host, db_port,
                                                                db_pwd))
    
    
    def execute_sql_query(self, query, **kwds):
        cursor = self.conn.cursor()
        cursor.execute(query.format(**kwds))

        return cursor.fetchall() 


    def _get_processing(self, dp_schema: str):
        res = self.execute_sql_query(get_processing_type, schema = dp_schema)
        
        if res != [] and res[0][0] is not None:
            return res[0][0]
        else:
            raise GetProcessingError

    def get_test_type(self, dp_schema: str):
        if (dp_schema.endswith('marts') or
            dp_schema.endswith('dds')):
            return 'marts'

        processing = self._get_processing(dp_schema)

        if not processing:
            raise 'Processing is not set'
        else:
            return processing
        
    def get_objects_dict(self):
        object_dict = {}

        object_types = {'tables': get_all_tables, 
                        'views': get_all_views, 
                        'functions': get_all_functions}
        
        for object_type in object_types:
            res = self.execute_sql_query(object_types[object_type], 
                                         schema=self.gp_schema)
                
            object_dict[object_type] = [elem[0] for elem in res]

        object_dict['common'] = []

        return object_dict