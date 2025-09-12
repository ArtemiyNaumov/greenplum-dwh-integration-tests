# Configuration

CLI app could by configured trough yaml formatted files

```yml

checks:
    # checks properties modifications
    <CHECK_ID_1>:
        level: WARNING # optional, level of the check, one of ('FAILURE', 'WARNING') 
        ignore:
            - object: schema.table1 # optional, list of database objects to be ignored by check
              valid_to: 2050-01-01  # date - end of ignore period
            - object: schema.table2
              valid_to: 2025-12-31
            ...
    <CHECK_ID_2>:
        level: WARNING
        ignore:
            ...
    ...

ignore_schema:
    # list of schemas to be ignored completely
    - schema: <schema>
      valid_to: 2050-01-01
    ...
```


## Usage

```sh
gp_dwh_integration_tests config path/to/config.yml [next command]
```
