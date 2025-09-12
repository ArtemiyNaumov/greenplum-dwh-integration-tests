from setuptools import setup, find_packages

setup(
    name='gp_dwh_integration_tests',
    description='DWH-DB integration tests',
    version='0.0.1',
    packages=find_packages(),  # list of all packages
    install_requires=[
        'chardet==5.1.0',
        'colorama==0.4.6',
        'fire==0.5.0',
        'Jinja2==3.1.2',
        'MarkupSafe==2.1.2',
        'pydantic==1.10.4',
        'pyparsing==3.0.9',
        'PyYAML==6.0',
        'six==1.16.0',
        'termcolor==2.2.0',
        'tqdm==4.64.1',
        'typing-extensions==4.4.0',
        'psycopg2-binary==2.9.9'
    ],
    python_requires='>=3.7',  # any python greater than 3.7
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'gp_dwh_integration_tests=gp_dwh_integration_tests.__main__:main'
        ]
    },
    author='Vladislav Iakovlev',
    keyword='',
    long_description='''
        GREENPLUM DWH-DB integration tests for sql and common antipatterns
    ''',
    long_description_content_type="text/markdown",
    dependency_links=[],
    author_email='vladislav.iakovlev@lemanapro.ru',
    classifiers=[]
)