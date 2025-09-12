import codecs
import os
from typing import List, Optional

from gp_dwh_integration_tests.checker import CheckResult, Checker
from gp_dwh_integration_tests.config import TEMPLATES_PATH
from gp_dwh_integration_tests.settings import Settings, SettingsLoader
from gp_dwh_integration_tests.utils import patch

import fire

from jinja2 import Environment, FileSystemLoader


class CheckerCli:
    '''
    CLI app for checking DWH-DB code for common antipatterns
    '''

    def __init__(self, checker: Checker):
        self.__checker = checker
        self.__settings = Settings()
        self.__jinja_env = Environment(
            loader=FileSystemLoader(TEMPLATES_PATH)
        )

    def _report(self, results: List[CheckResult]) -> None:
        template = self.__jinja_env.get_template('results.jinja2')
        print(template.render(results=results))

    def _github_report(self, results: List[CheckResult], schema: str, result_file: str) -> None:
        if all(res.status == 0 for res in results):
            return
        template = self.__jinja_env.get_template('github_report.jinja2')
        result_path = os.path.join('test_results',
                                   result_file.format(schema))
        with codecs.open(result_path, 'w+', 'utf-8') as f:
            f.write(template.render(results=results, schema=schema))

    def config(self, path: List[str]):
        """
        Configures checker from ini file
        Args:
            path: str, path to ini file
        """
        self.__settings = SettingsLoader().load(path)
        self.__checker.config(self.__settings.dict()['checks'],
                              self.__settings.dict()['ignore_schema'])
        return self

    def checks(self) -> None:
        '''
        Shows list of all checks descriptions
        '''

        template = self.__jinja_env.get_template('checks.jinja2')
        print(template.render(checks=self.__checker.checks()))

    def test(
        self,
        dp_schema: str,
        ignore: Optional[List[str]] = None,
        checks: Optional[List[str]] = None,
        label: Optional[str] = None,
        processing: Optional[List[str]] = None,
        force_dependencies: bool = False,
        progress_bar: bool = True,
        local_test = False
    ):
        '''
        Runs checks for files in defined path

        Args:
            path: path to dp--dwh-db repository copy
            ignore: list of checks to skip
            checks: list of checks to execute
            label: str, label of checks to execute
            processing: one of P1, P3, DP2.0, marts
            force_dependencies: flag for ignoring dependencies between checks
                (if True, dependencies will be ignored)
            progress_bar: bool, True, if progress bar needed, default True
        '''

        kwargs = patch(
            self.__settings.test.dict(),
            ignore=ignore,
            checks=checks,
            label=label,
            processing=processing,
            force_dependencies=force_dependencies,
            progress_bar=progress_bar
        )

        results = self.__checker.test(dp_schema, **kwargs)
        if results:
            self._report(results)
            if not(local_test):
                self._github_report(results, dp_schema, 'dwh-integration-tests.txt')
            if self.__checker.status:
                raise SystemExit(1)
            
    def compare_dev(
        self,
        changes: List,
        local_test = False        
    ):
        print("Changed files: ", changes)
        results = self.__checker.compare_dev(changes)
        if results:
            self._report(results)
            if not(local_test):
                self._github_report(results, 'dev_changes', 'compare-dev.txt')
            if self.__checker.status:
                raise SystemExit(1)


def cli(checker: Checker):
    '''
    Makes Fire CLI app from CheckerCli object

    Args:
        checker: Checker object
    '''
    cli_checker = CheckerCli(checker)
    return fire.Fire(cli_checker)
