# Berka Data Validation Sandbox

A local sandbox for practicing the PySpark and SQL patterns used for
data modeling, ETL, and validation against a banking data warehouse —
built against the Berka dataset (PKDD'99 Financial Dataset, via
[jlacko/berka-dataset](https://github.com/jlacko/berka-dataset)) rather
than production data, since the point was somewhere safe to make the
mistakes first.

## Layout

- `scripts/` — DDL for the raw and star-schema layers.
- `src/` — the loading, transform, and validation code the notebooks import.
- `notebooks/` — the pipeline itself: load and clean, build the star
  schema, validate it, investigate one validation failure in depth, then
  a client-behavior analysis on top of the finished model.
- `tests/` — pytest coverage for `src/` (partial — see `tests/README.md`).

Each directory has its own README with a file-by-file breakdown.

## Environment

MySQL 26.7, installed natively on macOS (not Docker) as a stand-in for
the work DWH — same wire protocol as StarRocks. PySpark runs local
(`local[*]`) over JDBC, no cluster. VS Code + Jupyter, one `.venv`.
Credentials and the JDBC driver path live in `.env`, never in code;
`.gitignore` excludes `.env`, `.venv/`, and the raw dataset CSVs — data
doesn't belong in git, even public, anonymized data.

## Setup

1. Create a `bank_sandbox` database, then run `scripts/tables_raw.sql`
   followed by `scripts/tables_trx_data_model.sql`.
2. `pip install -r requirements.txt`, fill in `.env`.
3. Run the notebooks in order, `01` through `05`.
4. `pytest` from the project root.

## Where this stands

The pipeline runs end to end. The validation suite in `03_validation.ipynb`
passes on every check except one Accuracy check, left failing on
purpose — `04_investigation_balance_mismatch.ipynb` root-causes it rather
than loosening the threshold to make it green. Test coverage currently
stops at the cleaning and config layer; `dimensional_model.py`,
`validations.py`, and `client_analytics.py` have none yet (`tests/README.md`
has the detail on why that's the part worth covering next).