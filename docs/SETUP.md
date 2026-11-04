# Local setup and reproduction

## 1. Prepare the tools

The review used macOS, Python 3.14.7, PySpark 4.2.0, and Java 17. This is an  
observed local environment, not a tested cross-platform support matrix.  
The dependency file is a full environment snapshot and includes `appnope`, a  
macOS-specific dependency. Installation on other operating systems is unverified.

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
java -version
python -m ipykernel install --user --name berka_dataset-sandbox --display-name "Python (berka_dataset-sandbox)"
python -m pytest -q
```

Select this kernel in your notebook editor. If Python workers use a different
interpreter, set `PYSPARK_PYTHON` to the absolute path of `.venv/bin/python` before
starting the editor/kernel.

The review did not reinstall the complete requirements snapshot. Its existing
environment had pandas 3.0.5, unlike the pinned 2.3.3, and produced a Spark warning.
A successful test run there is not proof of a fresh install. Record the actual
versions for your reproduction; do not silently replace pins if installation fails.

## 2. Obtain the source files

Download the eight data files from
[jlacko/berka-dataset](https://github.com/jlacko/berka-dataset), which identifies the
source as the PKDD'99 Discovery Challenge. Place them under the ignored
`berka-dataset-raw/` directory. Rename upstream `district.asc` to `district.csv`
without changing its semicolon-delimited contents, because `TABLES` expects that
filename. Do not resave the files through a spreadsheet application.

Expected layout:

```text
berka-dataset-raw/
  account.asc
  card.asc
  client.asc
  disp.asc
  district.csv
  loan.asc
  order.asc
  trans.asc
```

Each file must retain its header and semicolon separator. The district header is
`A1` through `A16`; the other mappings are listed in
[`src/table_configs.py`](../src/table_configs.py). Record the upstream revision or
file checksums when preparing an execution report. The local source counts alone
do not prove that files match an upstream revision byte for byte.

## 3. Configure the local database connection

Copy the example only if you do not already have a `.env`:

```bash
test -e .env || cp .env.example .env
```

Edit `.env` locally and set all six values:

| Key | Meaning |
| --- | --- |
| `DB_HOST` | Local MySQL host, such as `127.0.0.1` |
| `DB_PORT` | MySQL port, usually `3306` |
| `DB_NAME` | `bank_sandbox`, matching both DDL scripts |
| `DB_USER` | A dedicated local database user |
| `DB_PASSWORD` | That user's password |
| `JDBC_JAR_PATH` | Absolute path to the extracted Connector/J JAR |

The loader requires a nonempty password. Its JDBC URL disables TLS and enables
public-key retrieval for this local sandbox. Do not reuse these connection options
as a production configuration. Never print the configuration dictionary in saved
notebook output because it contains the password.

## 4. Create empty tables

Using a MySQL administrator connection, create a dedicated local database and
user with the permissions needed to create and load its tables. For the database:

```sql
CREATE DATABASE bank_sandbox;
```

Then run these commands from the project root with the configured user (replace
`berka_user` and connection arguments if needed). `-p` prompts for the password:

```bash
mysql -h 127.0.0.1 -P 3306 -u berka_user -p bank_sandbox < scripts/tables_raw.sql
mysql -h 127.0.0.1 -P 3306 -u berka_user -p bank_sandbox < scripts/tables_trx_data_model.sql
```

DBeaver can execute the same scripts. They contain `USE bank_sandbox` and plain
`CREATE TABLE`; they are not repeatable migrations. The optional commented reset
block must remain commented during initial setup.

## 5. Run the notebooks

Open notebooks with `notebooks/` as the kernel working directory. In a fresh kernel,
`from pathlib import Path; print(Path.cwd())` can confirm it. The existing imports
append `..`, so a kernel started at the repository root may fail to import `src`.

1. `01_load_and_clean.ipynb`: load the eight raw tables, once.
2. `02_build_star_schema.ipynb`: populate the eight model tables, once.
3. `03_validation.ipynb`: inspect raw counts and every quality-check result.
4. `04_investigation_balance_mismatch.ipynb`: investigate balance differences.
5. `05_client_behavior_analysis.ipynb`: inspect client features and segmentation.

Restart the kernel between notebooks. `01` and `02` explicitly stop Spark;
`03`–`05` otherwise leave it running until the kernel stops.

Writes append. If a load fails or was already completed, do not run the entire
pipeline again without checking table contents. See the
[DDL and reset notes](../scripts/README.md). No automatic rollback spans the full
pipeline. Notebooks `03`–`05` can be rerun against populated tables without
reloading them.

## 6. Capture evidence

Save aggregate results from `03`–`05`, the date, Git commit, source revision or
checksums, package versions, `java -version`, and MySQL `SELECT VERSION()` output.
Keep failed validation results visible. Do not call a known failure a pass.
Review saved output for credentials and local paths before committing it.
See the [validation guide](VALIDATION.md) for acceptance criteria.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| `.env` not found or missing values | File location and all six required keys |
| `ClassNotFoundException` for the JDBC driver | Absolute JAR path; restart the kernel after changing it |
| Java gateway fails | Java installation and the interpreter selected for Spark workers |
| Connection refused | MySQL service and the configured host/port |
| Access denied | Database user, password, and permissions |
| Missing `district.csv` | Rename upstream `district.asc` as described above |
| Duplicate-key insert failure | Existing data or a previous partial load; do not switch to overwrite |
| `ModuleNotFoundError: src` | Kernel working directory must be `notebooks/` |
| Accuracy result is `FAIL` | Inspect the mismatches and investigation; retain the 0.01 threshold |
