# tests

Unit tests for the modules in `../src/`, run with pytest.

## conftest.py

One fixture: a session-scoped local SparkSession (`local[1]`, single
core, named `berka-tests`). Session-scoped so the second or two of Spark
startup cost is paid once for the whole run, not once per test.

## test_spark_utils.py

Covers the bronze-layer cleaning functions — `clean_sentinels`,
`cast_columns`, `rename_columns`, and `prepare_table`, which chains all
three. Most tests build a one- or two-row DataFrame by hand rather than
touching the real dataset or database, so the whole file runs in
milliseconds and doesn't depend on anything being loaded first.

Two tests are worth calling out specifically. `test_cast_columns_keep_null_after_sentinel`
checks that a `?` converted to `NULL` by `clean_sentinels` survives a
subsequent cast to `decimal(5,2)` rather than blowing up or silently
becoming `0` — this is exactly the failure mode that broke the
`district` import originally. `test_prepare_table_with_account_config`
is the one integration-flavored test in the file: instead of a synthetic
column config, it runs `prepare_table` against the real
`rename_map("account")` / `type_map("account")` from `table_configs.py`,
so a typo or a dropped column in that config fails a test instead of
showing up as a load error later.

## test_table_configs.py

Pure-Python checks on `TABLES` and `LOAD_ORDER` — no Spark session
needed, so these run faster than anything in `test_spark_utils.py`.
Mostly structural: every table config has a `file`, a `db_table`, and a
non-empty `columns` list of 3-tuples, and `LOAD_ORDER` contains exactly
the same table names as `TABLES`, with `district` first since every
other table's foreign key eventually points back to it.
`test_district_rename_and_types` pins one specific mapping (`A12` →
`unemployment_rate_95` → `decimal(5,2)`) as a canary — if that column
list gets reordered or hand-edited later, this is what catches it.

## Running

`pytest` from the project root. Imports in the test files assume `src`
is importable from there, the same way the notebooks add `..` to
`sys.path`.

## Not covered yet

`dimensional_model.py`, `validations.py`, and `client_analytics.py` have
no tests, which is the riskier two-thirds of the codebase to leave
untested — `decode_birth_number`'s date-and-gender arithmetic and
`check_running_balance`'s sort key are exactly the kind of logic that
took a multi-step manual investigation to debug once (see
`04_investigation_balance_mismatch.ipynb`). A handful of small,
hand-built-DataFrame tests on those two functions specifically would
have caught the UROK ordering issue in seconds instead of several
notebook cells.

`write_to_mysql` / `read_from_mysql` in `spark_utils.py` aren't tested
either, but that's a different kind of gap — exercising them for real
needs a live database, which `01_load_and_clean.ipynb` and
`03_validation.ipynb` already do in practice, just not under pytest.