# scripts

DDL for both database layers. Run once, by hand, in DBeaver — nothing in
`src/` or `notebooks/` executes these.

## tables_raw.sql

The eight bronze tables `01_load_and_clean.ipynb` loads into. Types stay
close to the source: dates are `CHAR(6)`, not `DATE`, because the
source's raw `YYMMDD` strings don't parse cleanly and real date
conversion is deferred to the star-schema build. `NOT NULL` vs. nullable
was decided by looking at actual sample data rather than guessing —
where a column is nullable, the comment says why (Prague's `?` sentinel
in two `district` columns, a few genuinely optional fields in `order`
and `trans`).

Foreign keys and indexes exist here too, even though this is the "raw"
layer — deliberately, not an oversight. It means a broken reference
fails loudly at insert time in `01_load_and_clean.ipynb`, instead of
loading silently and only surfacing later as a Completeness failure in
`03_validation.ipynb`. Run before `01_load_and_clean.ipynb`; table order
in the file follows the same FK dependency chain as `LOAD_ORDER` in
`src/table_configs.py`.

## tables_trx_data_model.sql

The eight star-schema tables `02_build_star_schema.ipynb` writes into —
four dimensions, a bridge table, three facts. This is where dates
finally become real `DATE` columns, and where `dim_client.gender` /
`birth_date` live instead of the raw `birth_number`.

The commented-out block at the top is a reset: `TRUNCATE` on all eight
tables with `FOREIGN_KEY_CHECKS` off around it. Uncomment and run it
before re-running `02_build_star_schema.ipynb` from scratch — that
notebook's `write_to_mysql` calls only ever append, so re-running it
against already-populated tables produces duplicates rather than an
error.