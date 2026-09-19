# Notebooks

Five notebooks, run in order. Each one reads from and writes to the same
MySQL sandbox database (`bank_sandbox`); shared logic lives in `../src/`.

## 01_load_and_clean.ipynb

Loads the eight raw Berka `.asc` files, cleans them, and writes them into
MySQL bronze tables using the per-table configs in `src/table_configs.py`.
Cleaning handles two source quirks: `?` as a sentinel for missing numeric
values in `district.asc`, and inconsistent empty-vs-null handling in
`trans.asc` (`k_symbol`, `bank`, `account`).

Loads in FK-safe order — district → client → account → disp → card, loan,
order → trans. Row counts match the documented dataset sizes: 77 / 5,369 /
4,500 / 5,369 / 892 / 682 / 6,471 / 1,056,320.

## 02_build_star_schema.ipynb

Builds a Kimball-style star schema on top of the bronze tables: a
generated `dim_date` (1993–1998), `dim_district`, `dim_client` (decodes
`birth_number` into `birth_date` + `gender`), `dim_account`, a
`bridge_client_account` table for the client↔account many-to-many
relationship, and three fact tables — `fact_transactions`, `fact_loans`,
`fact_orders`. Transform logic is in `src/dimensional_model.py`.

## 03_validation.ipynb

The validation suite: referential integrity, primary key uniqueness,
not-null checks, and domain checks (`src/validations.py`), run against
every table in the star schema and reported as a single pandas table.

Everything passes except the transaction balance reconciliation check
(Accuracy). That failure is expected — see
`04_investigation_balance_mismatch.ipynb` for why, and don't "fix" it by
loosening the threshold.

## 04_investigation_balance_mismatch.ipynb

Root-causes the balance reconciliation failure from `03`. Two things
turned out to be going on, not one:

- `UROK` (interest) transactions are inserted by a monthly batch process
  with a `trans_id` range disjoint from regular transactions, which
  breaks `trans_id` as a same-day ordering key. Fixed by sorting `UROK`
  first on ties, implemented in `check_running_balance`. This alone only
  brought mismatches from 865,166 down to 795,450 — smaller than
  expected, which is what pushed the investigation from aggregate counts
  down to a single account (`account_id = 1033`).
- Even with ordering fixed, `UROK` amounts are systematically ~0.10 off
  from the actual balance change, and the error compounds across each
  account's later interest postings. Reads like a rounding convention
  from the original banking system rather than anything we can correct
  from the data available here.

## 05_client_behavior_analysis.ipynb

Builds a client-level transaction profile (attributed via `OWNER`
disposition) and an RFM segmentation (`ntile(4)` per dimension); helpers
in `src/client_analytics.py`.

One thing worth flagging for anyone reusing this: the raw "last
transaction date" per client is almost always the dataset's final day,
1998-12-31 — same UROK batch job as in `04`, hitting nearly every open
account on the last day of the month. Recency here is computed off
client-initiated transactions only (`k_symbol != UROK`) to avoid that.

Cross-tabbing RFM segment against `fact_loans.status` didn't show a
clean relationship — if anything, "Champions" had a *higher* problem-loan
rate than "At Risk" (2.7% vs. 1.0%). The underlying counts are small
(5–34 problem-loan clients per segment), so this isn't a result to lean
on in either direction.