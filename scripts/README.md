# Database definitions

Apply these scripts manually using a MySQL client or DBeaver before loading data.
Neither the Python modules nor the notebooks create the schema for you.
Both scripts select `bank_sandbox`; create that database first.

1. [tables_raw.sql](tables_raw.sql): eight source-shaped tables with primary keys,
   foreign keys, indexes, and explicit nullability. Dates remain source strings;
   conversion happens in notebook `02`. SQL column comments explain encodings and
   optional fields in English.
2. [tables_trx_data_model.sql](tables_trx_data_model.sql): four dimensions, a
   client-account bridge, and three fact tables. See the
   [model reference](../docs/DATA_MODEL.md) for grains and relationships.

These are initial DDL scripts, not migrations: rerunning `CREATE TABLE` against
existing tables fails. Inserts append to existing tables, preserving their DDL;
repeating a load normally fails on duplicate primary keys, rather than silently
creating duplicate keys.

## Optional reset block

The commented SQL at the top of `tables_trx_data_model.sql` is a **destructive reset
of the eight model tables only**. It is retained as an operational reference, not
executed setup. If you deliberately need to rebuild disposable model data:

1. Confirm the connection and selected database are the intended local sandbox.
2. Preserve anything you need before clearing it.
3. Select `bank_sandbox` before executing the reset block; the file's `USE` statement
   appears after the block.
4. Execute only the reset block, including restoration of `FOREIGN_KEY_CHECKS = 1`.
   Do not rerun the `CREATE TABLE` statements for existing tables.
5. Rerun notebook `02`, then validate with `03`.

This does not reset raw tables or make notebook `01` repeatable. A partial load
requires deliberate recovery. No reset was run during the documentation review.
