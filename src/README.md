# src

Shared code the notebooks import from. Nothing in here runs on its own —
each module backs one or more notebooks in `../notebooks/`.

## spark_utils.py

Session setup and all MySQL I/O. `load_config()` reads `.env` via
`find_dotenv()` rather than a hardcoded path, so it resolves correctly
regardless of which notebook (or which subfolder) calls it. `get_spark()`
builds a local `SparkSession` wired to the MySQL JDBC driver.
`read_from_mysql()` / `write_to_mysql()` wrap the JDBC read/write options;
`write_to_mysql()` always appends, never overwrites, because Spark's
`overwrite` mode drops and recreates the table with its own inferred
types — which would silently wipe out the primary keys, foreign keys, and
`NOT NULL` constraints from the DDL. Re-running a load notebook against
already-populated tables means truncating first, not switching modes.

`read_raw_csv()`, `clean_sentinels()`, `rename_columns()`, `cast_columns()`,
and `prepare_table()` are the bronze-layer cleaning pipeline used by
`01_load_and_clean.ipynb`. `prepare_table()` just chains the other three
in order — clean sentinels, rename, cast — for a given table's config
from `table_configs.py`.

## table_configs.py

Not really a module, more a data file. `TABLES` maps each of the eight
Berka source files to its destination table and a list of
`(source_column, target_column, spark_type)` triples; `LOAD_ORDER` fixes
the load sequence so nothing gets inserted before the table its foreign
key points to exists. `rename_map()` and `type_map()` just project that
column list into the two dicts `prepare_table()` needs.

Note that `district.csv`'s columns are `A1`...`A16` in the source, not
meaningful names — that's why this mapping is spelled out by hand rather
than inferred from matching column names.

## dimensional_model.py

Bronze-to-star transforms for `02_build_star_schema.ipynb`.
`build_dim_date()` generates the calendar dimension with `sequence()` +
`explode()` rather than loading it from anywhere. `parse_yymmdd_to_date()`
turns the source's raw `YYMMDD` strings into real dates by prefixing
`19` — fine for a dataset that ends in 1998, but it hardcodes the
century, so don't reuse it as-is against anything spanning 2000+.
`decode_birth_number()` is where the actual business logic lives: Czech
`birth_number` encodes gender by adding 50 to the month for female
clients, and this reverses that into separate `birth_date` and `gender`
columns.

## validations.py

The check functions behind `03_validation.ipynb`'s report — one per
DAMA-DMBOK dimension: `check_referential_integrity` (Completeness, via a
`left_anti` join), `check_uniqueness`, `check_not_null`,
`check_allowed_values` (Validity), `check_running_balance` (Accuracy),
`check_loan_after_account_open` (Consistency). Every one returns the same
`check` / `dimension` / `status` / `details` shape, which is why they
drop straight into a single pandas table without any reshaping.

`check_running_balance`'s ordering fix (UROK-first on same-day ties) is
the result of the investigation in `04_investigation_balance_mismatch.ipynb`
— read the docstring before touching the sort key.

## client_analytics.py

Client-level features for `05_client_behavior_analysis.ipynb`.
`build_client_transaction_profile()` attributes transactions to clients
through `bridge_client_account`, defaulting to the `OWNER` disposition
(`disposition_type="DISPONENT"` gives the other view). `add_behavioral_features()`
adds recency/frequency straight off that profile — its `recency_days`
turned out to be wrong for most clients (see `05`'s notes on the UROK
batch job landing on the dataset's last day) and is superseded by
`add_client_initiated_recency()`, which excludes `UROK` postings and adds
`recency_days_real` instead. Both columns end up on the same DataFrame;
`recency_days` is still there but nothing downstream reads it — worth
dropping it once the notebook settles, so nobody joins against it by
mistake later. `build_loan_status_flags()` attributes loans the same way
and flags clients with any loan in status `B` or `D` as `has_problem_loan`.