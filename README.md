# greenplum-dwh-integration-tests

Module for checking correctness of integration and data marts creation

## Features

- CLI app
- Additional configuration from file (ignoring paths, enabling/disabling checks). See [Configuration](docs/Configuration.md)
- Multiple alerting levels (`FAILURE`, `WARNING`)
- Checks for base antipatterns

## Installation

Installation from source

```sh
git clone https://github.com/ArtemiyNaumov/greenplum-dwh-integration-tests.git
cd greenplum-dwh-integration-tests
python setup.py install
```

Using docker

```sh
docker pull artemiynaumov/gp-dwh-integration-tests:latest
```

## Quick start

```sh
 gp_dwh_integration_tests config dwh-integration-tests.yml test sample_schema_ods
```

For more information go to [documentation](docs/index.md)
