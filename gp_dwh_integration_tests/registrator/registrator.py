import logging
from typing import Callable, Dict, List, Optional
import os

from gp_dwh_integration_tests.models import Check
from gp_dwh_integration_tests.registrator.exceptions import (
    DuplicateCheckIdsError,
    RegistrationError,
    RegistrationLoopError
)
from gp_dwh_integration_tests.utils import patch

from pydantic import ValidationError

from gp_dwh_integration_tests.config import SQL_PATH


class Registrator:
    '''
    Class for keeping checks information and checks execution order logic
    '''

    _checks: List[Check]
    logger: logging.Logger

    def __init__(self):
        self._checks = []
        self.logger = logging.getLogger(__name__)

    def is_duplicate(self, check: Check) -> bool:
        '''
        Checks if check with the same id already exists

        Args:
            check: Check, Check object to register

        Returns:
            bool, True, if check with the same id already exists
        '''

        for registered_check in self._checks:
            if registered_check.id == check.id:
                return True

        return False

    def creates_dependency_loop(self, check: Check) -> bool:
        '''
        Detects loop in checks dependencies

        Args:
            check: Check, Check object to register

        Returns:
            bool, True if loop detected
        '''

        queue = [check]
        visited = []
        checks = {
            check.id: check
            for check in self._checks
        }
        checks[check.id] = check

        while queue:
            node = queue.pop(0)
            if node.id in visited:
                return True

            visited.append(node.id)

            if node.depends_on is not None:
                for id in node.depends_on:
                    if id in checks:
                        queue.append(checks[id])

        return False

    def register(
        self,
        func: Callable,
        id: str,
        description: Optional[str] = None,
        sql_path: str = None,
        ignore: Optional[List[str]] = None,
        level: str = 'FAILURE',
        depends_on: Optional[List[str]] = None,
        label: Optional[str] = None,
        processing: Optional[List[str]] = None
    ) -> Check:
        '''
        Registers check function inside registrator object

        Args:
            func: Callable, wrapped check function
            id: str, check id
            description: str, check description
            path: List[str], list of paths patterns to execute check
            ignore: List[str], list of path to be ignored by check
            level: str, level of the check, one of ('FAILURE', 'WARNING')
            depends_on: List[str], list of checks ids which will deny
                check execution if fail
            label: str, check's extra classification
            processing: one of P1, P3, DP2.0, marts

        Returns:
            Check, Check object
        '''
        check = Check(
            id=id,
            description=description,
            level=level,
            ignore=ignore,
            sql_path=SQL_PATH,
            callable=func,
            depends_on=depends_on,
            label=label,
            processing=processing
        )

        if self.is_duplicate(check):
            raise DuplicateCheckIdsError(
                f'Check with id {check.id} already exists'
            )

        if self.creates_dependency_loop(check):
            raise RegistrationLoopError(
                f'Dependencies loop detected for check {check.id}'
            )

        self._checks.append(check)
        self.logger.debug(f'Check {id} registered')
        return check

    def patch_check(self, check: Check, **kwargs) -> Check:
        '''
        Creates new check with updated attributes

        Args:
            check: check to patch
            **kwargs: new attributes values

        Returns:
            patched check
        '''

        base = check.dict()

        if 'ignore' in kwargs and kwargs['ignore'] is not None and base['ignore'] is not None:
            kwargs['ignore'] = kwargs['ignore'] + base['ignore']

        patched = Check(**patch(kwargs, **base))
        if self.creates_dependency_loop(patched):
            raise RegistrationLoopError(
                f'Dependencies loop detected for check {check.id}'
            )

        return patched

    def patch(self, settings: Dict[str, dict]):
        '''
        Patches registered checks by passed settings

        Args:
            settings: dict with checks ids as keys and checks attributes
                as values
        '''

        for i, check in enumerate(self._checks):
            if check.id in settings:
                self._checks[i] = self.patch_check(
                    check,
                    **settings[check.id]
                )

    def checks(
        self,
        dp_schema: Optional[str] = None,
        ignore: Optional[List[str]] = None,
        checks: Optional[List[str]] = None,
        label: Optional[str] = None,
        processing: Optional[List[str]] = None
    ) -> List[Check]:
        '''
        Returns list of registered checks

        Args:
            ignore: List[str], list of checks ids to skip
            checks: List[str], list of checks ids to return

        Returns:
            List[Checks], list of registered Check objects
        '''

        return [
            check
            for check in self._checks
            if ((checks is None or check.id in checks)
                and (label is None or check.label in label)
                and (processing is None or processing in check.processing)
            )
        ]


    def checks_ordered(
        self,
        dp_schema: Optional[str] = None,
        ignore: Optional[List[str]] = None,
        checks: Optional[List[str]] = None,
        label: Optional[str] = None,
        processing: Optional[List[str]] = None
    ) -> List[Check]:
        '''
        Returns list of registered checks in execution order

        Args:
            ignore: List[str], list of checks ids to skip
            checks: List[str], list of checks ids to return

        Returns:
            List[Checks], list of registered Check objects
                in execution order
        '''

        checks_set = {
            check.id: check
            for check in self.checks(dp_schema, ignore, checks, label, processing)
        }

        checks_order = []
        while checks_set:
            pop_ids = set()
            for check_id, check in checks_set.items():
                if check.depends_on is None:
                    checks_order.append(check)
                    pop_ids.add(check_id)
                elif all(
                    id not in checks_set
                    for id in check.depends_on
                ):
                    checks_order.append(check)
                    pop_ids.add(check_id)

            for check_id in pop_ids:
                del checks_set[check_id]

        return checks_order
