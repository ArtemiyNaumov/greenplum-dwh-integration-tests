import logging

import logging
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from gp_dwh_integration_tests.registrator import RegistrationError, Registrator

from gp_dwh_integration_tests.utils import import_submodules

from gp_dwh_integration_tests.config import CHECKS_PATH, BASE_PATH

from gp_dwh_integration_tests.query import *

from gp_dwh_integration_tests.registrator.exceptions import (
    GetProcessingError
)

import os


from gp_dwh_integration_tests.models import (
    Check,
    CheckLevel,
    CheckResult,
    Connection,
    STATUS_MAPPING
)

from tqdm import tqdm

class Checker:
    '''Class for schema checking logic realisation'''

    _registrator: Registrator
    _results: list
    _logger: logging.Logger = logging.getLogger(__name__)
    status_maping: Dict[CheckLevel, int] = STATUS_MAPPING
    status: int = 0
    _ignore_schema: List[str] = []

    def __init__(self):
        self._results = []
        self._registrator = Registrator()

    def import_base_checks(self) -> None:
        import_submodules(CHECKS_PATH)

    def config(self, settings: Dict[str, dict],
               ignore_schema: str) -> None:
        '''
        Updates attributes of checks according to passed settings

        Args:
            settings: dict, checks settings
        '''
        self._ignore_schema = ignore_schema
        self._registrator.patch(settings)

    def check(
        self,
        id: str = None,
        description: Optional[str] = None,
        sql_path: Optional[List[str]] = None,
        ignore: Optional[List[str]] = None,
        level: str = 'FAILURE',
        depends_on: Optional[List[str]] = None,
        processing: Optional[List[str]] = None,
        label: Optional[str] = None
    ) -> Callable:
        '''
        Returns decorator for wrapping check function

        Args:
            id: str, check id
            description: str, check description
            path: List[str], list of paths patterns to execute check
            sql_path: List[str], list of path to be ignored by check
            level: str, level of the check, one of ('FAILURE', 'WARNING'),
                FAILURE by default
            depends_on: List[str], list of checks ids which will deny
                check execution if fail
        '''

        def decorator(func: Callable) -> Callable:
            '''
            Decorator for wrapping check function
            '''
            check_id = id or func.__name__
            check_description = description or func.__doc__
            try:
                self._registrator.register(
                    func,
                    id=check_id,
                    description=check_description,
                    sql_path=sql_path or ['**'],
                    ignore=ignore,
                    level=level,
                    depends_on=depends_on,
                    processing=processing,
                    label=label
                )
            except RegistrationError:
                raise

            return func

        return decorator

    def _set_status(self, check_result: CheckResult) -> None:
        '''
        Updates repository checking result

        Args:
            check_result: CheckResult, result of current check
        '''

        if check_result.status == self.status_maping[CheckLevel.FAILURE]:
            self.status = self.status_maping[CheckLevel.FAILURE]

    def _tasks(
        self,
        dp_schema: str,
        checks_order: List[Check],
        ignore: Optional[List[str]] = None,
        object_dict: Dict[str, List[str]] = None,
        force_dependencies: bool = False
    ) -> List[Tuple[Check, str, str, bool]]:
        '''
        Returns list of file paths and tasks mapping

        Args:
            path: Path, path to apply checks
            checks: List[Check], list of checks needed to apply
            force_dependencies: bool, flag for ignoring dependencies
                between checks (if True, dependencies will be ignored)
        '''

        tasks = []

        for object_type in object_dict:
            if object_type != 'common':
                for check in [c for c in checks_order if c.label == object_type]:

                    for obj in object_dict[object_type]:

                        if (check.ignore is None or
                            ('.'.join([dp_schema, obj]) not in check.ignore and
                            obj not in check.ignore)):

                            tasks.append({'check': check,
                                          'gp_conn': self.gp_conn,
                                          'sql_path': check.sql_path,
                                          'dp_schema': dp_schema,
                                          'dp_obj': obj})
                            
            else:
                for check in [c for c in checks_order if c.label == object_type]:
                    tasks.append({'check': check,
                                  'gp_conn': self.gp_conn,
                                  'sql_path': check.sql_path,
                                  'dp_schema': dp_schema,
                                  'dp_obj': None})

        return tasks

    def test(
        self,
        dp_schema: str,
        ignore: Optional[List[str]] = None,
        checks: Optional[List[str]] = None,
        label: Optional[str] = None,
        processing: Optional[List[str]] = None,
        force_dependencies: bool = False,
        progress_bar: bool = True
    ) -> List[CheckResult]:
        '''
        Runs checks for files in defined path

        Args:
            path: str, path to dp--dwh-db repository copy
            ignore: List[str], list of checks ids to skip
            checks: List[str], list of checks ids to execute
            label: str, label of checks to execute
            processing: List[str], on of P1, P3, DP2.0, marts
            force_dependencies: bool, flag for ignoring dependencies
                between checks (if True, dependencies will be ignored)
            progress_bar: bool, True, if progress bar needed, default True

        Returns:
            List[CheckResult], list of checks results
        '''

        self._results = []
        self.status = 0

        schemas = [dp_schema] if isinstance(dp_schema, str) else dp_schema

        for schema in schemas:
            self.gp_conn = Connection(schema)
            checks = checks
            label = label or ('tables', 'views', 
                            'roles', 'functions', 'common')
            
            if schema in self._ignore_schema:
                continue
            
            try:
                processing = self.gp_conn.get_test_type(schema)
            except GetProcessingError:
                res = {
                    'id': 'C000',
                    'status': 1,
                    'exception': 'Can not get processing type from schema comment for {}'.format(schema)
                }
                self.status = 1
                return [CheckResult(**res)]
            
            checks_order = self._registrator.checks_ordered(schema, ignore, checks, label, processing)
            
            object_dict = self.gp_conn.get_objects_dict()
            
            tasks = self._tasks(schema, 
                                checks_order,
                                ignore,
                                object_dict,
                                force_dependencies)
            
            if progress_bar:
                tasks = tqdm(tasks)
            
            for task in tasks:
                result = task['check'].apply(task['gp_conn'],
                                    task['dp_schema'], task['dp_obj'])
                self._set_status(result)
                self._results.append(result)

        return self._results

    
    def compare_dev(
        self,
        changes: List
    ):
        # Build objects_dict compatible with Check interface
        all_changed_objects = {}

        for obj in changes:
            obj_splitted = obj.split('/')
            if obj_splitted[0] == 'schemas':
                if obj_splitted[-2] in ('tables', 'views', 'functions'):
                    obj_name = obj_splitted[-1].split('.')[0]
                    obj_type = obj_splitted[-2]
                    obj_schema = obj_splitted[-3]

                    if obj_schema not in all_changed_objects:
                        all_changed_objects[obj_schema] = {
                            'tables': [], 
                            'views': [], 
                            'functions': [],
                            'common': []
                        }

                    all_changed_objects[obj_schema][obj_type].append(obj_name)

        gp_dev_credentials = {
            'db_host': os.environ.get('DEV_DB_HOST'),
            'db_port': os.environ.get('DEV_DB_PORT'),
            'db_name': os.environ.get('DEV_DB_NAME'),
            'db_user': os.environ.get('DEV_DB_USER'),
            'db_pwd': os.environ.get('DEV_DB_PWD')
        }

        dev_conn = Connection(**gp_dev_credentials)

        self._results = []
        self.status = 0

        for schema in all_changed_objects:
            self.gp_conn = Connection(schema)

            checks_order = self._registrator.checks_ordered(schema, ignore=None, checks=None, label=None, processing='dev')

            tasks = self._tasks(schema, 
                                checks_order,
                                ignore=None,
                                object_dict=all_changed_objects[schema],
                                force_dependencies=False)
            
            for task in tasks:
                result = task['check'].apply(task['gp_conn'],
                                    task['dp_schema'], task['dp_obj'], dev_conn)
                self._set_status(result)
                self._results.append(result)

        print(self._results)

        return self._results
