# CLI reference
`gp_dwh_integration_tests` - CLI app for checking GREENPLUM DWH objects consistency

## Synopsis

```sh    
gp_dwh_integration_tests <COMMAND>
```

## Commands

### `checks`

Shows list of all existing checks descriptions

**Synopsis:**

### `config`

Reads the configuration yaml file

**Synopsis:**

```sh
gp_dwh_integration_tests config [PATH]
```

**Positional arguments:**

argument | type | description
:-- | :-- | :--
`PATH` | string | path to configuration file

**Examples**

```sh
$ cat > dwh-integration-tests.yml << EOL
checks:
    T001:
        level: WARNING
        ignore: 
            - schema.table2
    T002:
        level: WARNING

$ gp_dwh_integration_tests config dwh-integration-tests.yml test schema

[T003]  | WARNING
Exception: Type of schema.table.column should be timestamp with time zone.

[T004]  | WARNING
Exception: Tables should be created in WARM tablespace
if possible. Check tablespace for schema.table

[T005]  | WARNING
Exception: Table schema.table is not used in any view.
If thats's a feature, just add it to ignore


checks executed: 31; warnings: 0; failed: 3; succeed: 28 [90.32%]
CHECKS FAILED
...
```

### `test`

Runs checks for files in defined path

**Synopsis:**

```sh
gp_dwh_integration_tests test PATH <flags>
```

**Positional arguments:**

argument | type | description
:-- | :-- | :--
`PATH` | string | path to local copy of [greenplum-dwh-template](https://github.com/ArtemiyNaumov/greenplum-dwh-template) repository

**Flags:**

flag | type | default | description
:-- | :-- | :-- | :--
`-i`, `--ignore` | list | `None` | comma delimited checks ids to ignore
`-c`, `--checks` | list | `None` | comma delimited checks ids to execute (only)
`-l`, `--label` | str | `None` | label of checks to execute
`-f`, `--force_dependencies`, `--force-dependencies` | bool | `False` | flag for ignoring dependencies between checks (if True, dependencies will be ignored)
`-p`, `--progress_bar`, `--progress-bar` | bool | `True` | True, if progress bar needed, default True
