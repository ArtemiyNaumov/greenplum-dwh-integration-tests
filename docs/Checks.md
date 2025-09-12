# GREENPLUM DWH integration tests

## Contents

- [C000](#C000)
- [C001](#C001)
- [C002](#C002)
- [C003](#C003)
- [C004](#C004)
- [C005](#C005)
- [D001](#D001)
- [D002](#D002)
- [D003](#D003)
- [D004](#D004)
- [D005](#D005)
- [T001](#T001)
- [T002](#T002)
- [T003](#T003)
- [T004](#T004)
- [T005](#T005)
- [T006](#T006)
- [T007](#T007)
- [T008](#T008)
- [T009](#T009)
- [T010](#T010)
- [T011](#T011)
- [T012](#T012)
- [V001](#V001)
- [V002](#V002)
- [V003](#V003)
- [V004](#V004)

## [FAILURE] C000 <a class="anchor" id="C000"></a>

Checks if processing type is set in schema comment for ods schemas.
Each ods schema should have a comment with processing type used for it's integration.

SQL commands to add this comment:

DP 2.0 -- comment on schema <source>_ods is 'DP2.0'
Processing 3 -- comment on schema <source>_ods is 'P3'
Processing 1 -- comment on schema <source>_ods is 'P1'

Label: `common`

Processing:
 - DP2.0

## [FAILURE] C001 <a class="anchor" id="C001"></a>

Checks if schema has been created. 

Label: `common`

Processing:
 - DP2.0
 - marts

## [FAILURE] C002 <a class="anchor" id="C002"></a>

Checks if default roles have been created for the schema. Mandatory roles are:

- <schema>_w
- <schema>_r'
- <schema>_x'
- <schema>_rw'
- <schema>_rwx

Label: `common`

Processing:
 - DP2.0
 - marts

## [WARNING] C003 <a class="anchor" id="C003"></a>

Checks if rwx permission is granted to at least one etlbot

Label: `common`

Processing:
 - DP2.0
 - marts


## [FAILURE] C004 <a class="anchor" id="C004"></a>

Checks if pxf_select is granted to etlbot. Mandatory for DP 2.0 processing.

Label: `common`

Processing:
 - DP2.0


## [FAILURE] C005 <a class="anchor" id="C005"></a>

Checks if r, w, x roles are granted to all objects of the schema

Label: `common`

Processing:
 - DP2.0
 - marts


## [WARNING] D001 <a class="anchor" id="D001"></a>

Checks table existence in both environments and it's owners

Label: `tables`

Processing:
 - dev

## [WARNING] D002 <a class="anchor" id="D002"></a>

Checks attributes of a table

Label: `tables`

Processing:
 - dev

## [WARNING] D003 <a class="anchor" id="D003"></a>

Checks table existence in both environments and it's owners

Label: `views`

Processing:
 - dev


## [WARNING] D004 <a class="anchor" id="D004"></a>

Checks attributes of a table

Label: `views`

Processing:
 - dev


## [WARNING] D005 <a class="anchor" id="D005"></a>

Checks function existence in both environments and it's owners

Label: `functions`

Processing:
 - dev


## [WARNING] T001 <a class="anchor" id="T001"></a>

Checks if tables in ods and marts are column-oriented 

Label: `tables`

Processing:
 - DP2.0
 - marts


## [WARNING] T002 <a class="anchor" id="T002"></a>

Checks if every column of a table has the same storage parameters as 
the whole table

Label: `tables`

Processing:
 - DP2.0
 - marts

## [FAILURE] T003 <a class="anchor" id="T003"></a>

Checks if tables have all mandatory columns for DP2.0 integration

Label: `tables`

Processing:
 - DP2.0

 ## [WARNING] T004 <a class="anchor" id="T004"></a>

Checks if the table is on the warm tablespace

Label: `tables`

Processing:
 - DP2.0
 - marts

 ## [WARNING] T005 <a class="anchor" id="T005"></a>

Check if table is used by at least one view

Label: `tables`

Processing:
 - DP2.0
 - marts

 ## [FAILURE] T006 <a class="anchor" id="T006"></a>

Check if table is partitioned

Label: `tables`

Processing:
 - DP2.0
 - marts

 ## [FAILURE] T007 <a class="anchor" id="T007"></a>

Mandatory attributes for P1 integration

Label: `tables`

Processing:
 - P1

 ## [FAILURE] T008 <a class="anchor" id="T008"></a>

Mandatory attributes for P3 integration

Label: `tables`

Processing:
 - P3

 ## [FAILURE] T009 <a class="anchor" id="T009"></a>

Checks if type of the partitioning column is either timestamp or date

Label: `tables`

Processing:
 - DP2.0
 - marts
 - P3
 - P1

 ## [FAILURE] T010 <a class="anchor" id="T010"></a>

Checks if tables do not have default values

Label: `tables`

Processing:
 - DP2.0
 - marts
 - P3

 ## [WARNING] T011 <a class="anchor" id="T011"></a>

Checks if tables' columns do not have `NOT NULL` constraints

Label: `tables`

Processing:
 - DP2.0
 - marts
 - P3

 ## [WARNING] T012 <a class="anchor" id="T012"></a>

Checks if tables columns' names do not contain
non-latin and non-numeric characters

Label: `tables`

Processing:
 - DP2.0
 - marts
 - P3

## [FAILURE] V001 <a class="anchor" id="V001"></a>

Checks if views have all mandatory columns for DP2.0 integration

Label: `views`

Processing:
 - DP2.0


## [WARNING] V002 <a class="anchor" id="V002"></a>

Checks if columns and views have the same columns

Label: `views`

Processing:
 - DP2.0
 - marts

## [WARNING] V003 <a class="anchor" id="V003"></a>

Mandatory attributes for P1 integration

Label: `views`

Processing:
 - P1

## [WARNING] V004 <a class="anchor" id="V004"></a>

Mandatory attributes for P3 integration

Label: `views`

Processing:
 - P3
