import os
import sys

from importlib.util import module_from_spec, spec_from_file_location


def patch(base: dict, **kwargs) -> dict:
    '''
    Helper for replacing dict values
    '''

    for key, value in kwargs.items():
        base_value = base.get(key)
        if base_value is None:
            base[key] = value

    return base 

def import_submodules(path: str):
    '''
    Helper for importing checks

    Args:
        path: str, path to checks directory
    '''

    if os.path.exists(path):
        for subpath, _, files in os.walk(path):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(subpath, file)
                    module_name = file[:-3]
                    spec = spec_from_file_location(module_name, filepath)
                    module = module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)
    else:
        raise ImportError('Path {} does not exists'.format(path))