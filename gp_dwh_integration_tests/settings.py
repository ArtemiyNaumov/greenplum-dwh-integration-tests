from datetime import date
from typing import Dict, List, Optional

from pydantic import BaseModel

import yaml


class CheckSettings(BaseModel):
    '''Check settings model'''
    level: Optional[str] = None
    ignore: Optional[List[str]] = None
    depends_on: Optional[List[str]] = None
    label: Optional[str] = None
    processing: Optional[List[str]] = None


class TestCommandSettings(BaseModel):
    '''Test command settings model'''
    ignore: Optional[List[str]] = None
    checks: Optional[List[str]] = None
    label: Optional[str] = None
    processing: Optional[List[str]] = None
    force_dependencies: Optional[bool] = True
    progress_bar: Optional[bool] = False


class TestParallelCommandSettings(TestCommandSettings):
    '''Test-parallel command settings model'''
    num_executors: Optional[int] = None


class Settings(BaseModel):
    '''Settings model'''
    test: TestCommandSettings = TestCommandSettings()
    test_parallel: TestParallelCommandSettings = TestParallelCommandSettings()
    checks: Dict[str, CheckSettings] = dict()
    ignore_schema: List[str] = []


class SettingsLoader:
    '''Settings loader for yaml formatted files'''
    _sections = (
        'test',
        'test_parallel',
        'checks'
    )

    def load(self, path: str) -> Settings:
        path_list = path.split(',')
        config_list = []
        for elem in path_list:
            with open(elem) as f:
                settings = yaml.safe_load(f)
                config_list.append(settings)

        config = self._merge_configs(config_list)

        return Settings(**config)
    
    def _merge_configs(self, config_list):
        today = date.today()
        merged_config = {'checks': {}, 'ignore_schema': []}

        for config in config_list:
            if config['checks']:
                for check in config['checks']:

    #               Add all unexpired paths to ignore_path_list
                    ignore_path_list = []
                    for ignore_path in config['checks'][check]['ignore']:
                        if ignore_path['valid_to'] > today:
                            ignore_path_list.append(ignore_path['object'])

                    ignore_path_list = list(set(ignore_path_list))
                    
                    if not(check in merged_config['checks']):                 
                        merged_config['checks'][check] = {'ignore': ignore_path_list}
                    else:
                        for path in ignore_path_list:
                            if not(path in merged_config['checks'][check]['ignore']):
                                merged_config['checks'][check]['ignore'].append(path)

            if config['ignore_schema']:
                for ignore_schema in config['ignore_schema']:
                    if (ignore_schema['valid_to'] > today and 
                        ignore_schema['schema'] not in merged_config['ignore_schema']):

                        merged_config['ignore_schema'].append(ignore_schema['schema'])

        return merged_config

    