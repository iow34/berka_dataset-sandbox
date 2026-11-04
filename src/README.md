# Python modules

The notebooks orchestrate execution; these modules provide reusable functions.
`__init__.py` is an empty package marker.

| Module | Responsibility | Important behavior |
| --- | --- | --- |
| [spark_utils.py](spark_utils.py) | `.env` loading, local Spark, CSV cleaning, JDBC I/O | Raw files resolve relative to the discovered `.env`; database writes append |
| [table_configs.py](table_configs.py) | Eight source mappings, Spark types, load order | Expects `district.csv`; `order` is quoted for MySQL |
| [dimensional_model.py](dimensional_model.py) | Calendar, source dates, birth-number decoding | Assumes the 1900s for encoded dates; not a general date or ID parser |
| [validations.py](validations.py) | Referential, uniqueness, null, domain, balance, and chronology checks | Returns report data; does not fail the pipeline automatically |
| [client_analytics.py](client_analytics.py) | Transaction profiles, activity features, loan flags | Defaults to `OWNER` attribution; RFM scoring itself lives in notebook `05` |

## Cleaning and database I/O

`prepare_table()` replaces sentinels, renames columns, selects the configured
columns, and casts their types. It does not trim all whitespace, deduplicate rows,
or validate arbitrary malformed source values.

`get_spark()` uses `local[*]` and the configured Connector/J JAR. `load_config()`
requires all six keys shown in [`.env.example`](../.env.example). Its JDBC URL
disables TLS for the local sandbox; this is not a production connection template.

`write_to_mysql()` uses a batch size of 10,000 and append mode. Existing database
constraints remain in place; duplicate keys may reject a rerun. There is no
cross-table transaction, checkpoint, incremental-load logic, or automatic recovery.

## Validation contracts

Single checks return `check`, `dimension`, `status`, and `details`.
`check_not_null()` returns one such dictionary per column.
`check_running_balance()` returns `(result, mismatches_dataframe)`.

Domain checks exclude SQL NULLs from their invalid-value count. Chronology checks
use inner joins and omit unresolved keys. Separate not-null and referential checks
are therefore necessary. Balance reconciliation assumes complete account history,
a zero opening balance, `PRIJEM` inflows, other types as outflows, and interest-first
same-day ordering. See [validation scope](../docs/VALIDATION.md).

## Analytics interpretation

`build_client_transaction_profile()` uses inner joins; clients without matching
transactions are absent. Selected links can attribute one account's transactions
to more than one client if the bridge contains multiple links of that type.

`add_behavioral_features()` uses all postings. `add_client_initiated_recency()`
adds a second recency field excluding `UROK` but retaining NULL `k_symbol`. The
name expresses an approximation: it cannot distinguish all automated postings.
Clients without a qualifying posting receive NULL recency.

`build_loan_status_flags()` flags any loan with status `B` or `D`. Notebook `05`
fills missing flags with zero, including clients without loans. Its segment-level
percentage is therefore not a default rate among borrowers.
