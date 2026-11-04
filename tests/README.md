# Automated tests

Run from the repository root after installing the dependencies and configuring
Java for Spark:

```bash
python -m pytest -q
```

No MySQL instance, JDBC driver, `.env`, or raw dataset is needed by these tests.
Spark still starts a local JVM; this is not a pure-Python test suite.

## Files and coverage

| File                                           | Coverage                                                                                                                                                     |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [conftest.py](conftest.py)                     | Session-scoped `local[1]` Spark fixture, stopped after the session                                                                                           |
| [test_spark_utils.py](test_spark_utils.py)     | Seven tests: sentinel replacement, ordinary text preservation, integer/decimal casts, NULL preservation, renaming, preparation, and the real account mapping |
| [test_table_configs.py](test_table_configs.py) | Three tests: table-set agreement and district-first order, a district mapping/type, and basic configuration structure                                        |
| __[init__.py](__init__.py)                     | Empty package marker                                                                                                                                         |

Configuration tests verify selected structural properties, not every dependency
in the load order or every source column. Cleaning tests use small in-memory
DataFrames, not the full dataset.

## Latest review result

On **2026-11-01**, all **10 tests passed in 14.05 seconds** with Python 3.14.7,
PySpark 4.2.0, Java 17, and pytest 9.1.1. The existing local environment contained
pandas 3.0.5, while `requirements.txt` pins 2.3.3. Spark emitted one warning about
pandas 3 compatibility. The tests do not validate pandas-based reporting.

Pytest was installed in an isolated temporary tool directory for this review;  
the project's `.venv` and dependency pins were not changed. This run verifies  
the existing tests, not a clean installation of all pinned requirements.
