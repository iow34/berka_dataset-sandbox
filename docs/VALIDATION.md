# Validation scope and evidence

## Evidence reviewed on 2026-11-01

All 25 tracked files were reviewed, including the five notebooks, SQL DDL, source modules,  
tests, dependency snapshot, ignore rules, README files, and the ERD image.

| Evidence | Result | What it does not prove |
| --- | --- | --- |
| Local source-file counts | All eight matched the expected counts below | Successful database load or equality with a specific upstream revision |
| Existing pytest suite | 10 passed in 14.05 seconds; one pandas compatibility warning | Full model, JDBC, validation, or analytics correctness |
| Existing notebooks | All five have empty outputs | Historical narrative counts are not independently auditable execution results |
| Local MySQL connectivity | Configured local port unavailable | No fresh database or notebook validation was possible |
| Runtime logic preservation | Python ASTs match after removing docstrings; notebook code cells unchanged | Does not resolve pre-existing model/analysis limitations |

Tests used Python 3.14.7, PySpark 4.2.0, Java 17, pandas 3.0.5, and pytest 9.1.1.
Pytest was provided from an isolated temporary tool directory, without installing
it into the existing project environment. `requirements.txt` instead pins pandas
2.3.3. The review did not perform a fresh installation of every pinned dependency.

## Source counts

These counts exclude the header and were read directly from local files using a
semicolon-delimited CSV reader. Notebook `03` separately compares database counts
with the same expectations when executed.

| Raw table | Local filename | Count |
| --- | --- | ---: |
| district | district.csv | 77 |
| client | client.asc | 5,369 |
| account | account.asc | 4,500 |
| disp | disp.asc | 5,369 |
| card | card.asc | 892 |
| loan | loan.asc | 682 |
| order | order.asc | 6,471 |
| trans | trans.asc | 1,056,320 |

## Model report coverage

Notebook `03` builds **28 report rows** in five quality categories. The categories
are an organizing convention, not a claim of formal DAMA compliance.

| Category | Report rows | Implemented scope |
| --- | ---: | --- |
| Completeness / referential integrity | 9 | All nine FK relationships in the model |
| Uniqueness | 6 | Client, account, transaction, loan, order, and bridge keys |
| Completeness / required fields | 7 | Three client fields and four transaction fields |
| Validity / domains | 4 | Client gender, transaction type, loan status, disposition type |
| Accuracy / running balances | 1 | Signed cumulative sum versus stated balance; 0.01 tolerance |
| Consistency / chronology | 1 | Loan date must not precede account opening |

The eight raw-table count comparisons print separately; they are not part of the
28-row pandas report. `dim_date` and `dim_district` uniqueness are enforced by DDL
but are not separately checked by the notebook's uniqueness loop.

Checks return/display `OK` or `FAIL`; raw counts display `OK` or `MISMATCH`.
A failed result does not automatically stop the notebook or fail a CI job.

## Interpretation boundaries

- Domain checks use SQL three-valued logic: NULL does not count as an invalid
domain value. Run explicit not-null checks for required fields.
- The chronology check uses inner joins; referential checks must detect rows
omitted by those joins.
- Balance reconciliation assumes complete account history, zero opening balances,
`PRIJEM` as inflow, all other types as outflow, and interest-first same-day order.
Source transaction IDs are not an authoritative intraday timestamp.
- Notebook `04`, Step 2, calls `F.round` without a scale, rounding differences to
whole units. It is a coarse exploratory check and cannot establish 0.10-scale
effects. The later fixed-order pairwise check uses two decimal places.
- The daily diagnostic selects the highest transaction ID as the final posting,
so it inherits the ordering uncertainty it investigates.
- Source-rounding and separate-batch explanations remain hypotheses. Historical
mismatch counts are recorded with their limitations in [CASE_STUDY.md](CASE_STUDY.md).
- RFM uses net cash flow, not customer revenue. NULL recency, untied quartile order,
account ownership, and the loan denominator require care; see the case study.

## How to retain reproducible results

1. Follow [SETUP.md](SETUP.md), record the Git commit, and identify the input files

   by upstream revision or checksums. Record actual Python, Java, MySQL, Spark, and
    pandas versions. Do not include passwords or the full connection configuration.
2. If tables are already populated, inspect them and run read-only notebooks

   `03`–`05`; do not reload `01` and `02` just to obtain screenshots.
3. Save the eight raw counts and the full 28-row report from `03`. Account for every

   failure; keep a balance failure visible until its cause is supported by evidence.
4. Save naive and revised mismatch counts, affected-account counts, and pairwise

   aggregates from `04`. Explain why cumulative counts differ from independent
    errors. Retain enough supporting evidence for the sample-account reasoning.
5. Save profile counts, NULL-recency counts, segment sizes, and loan denominators

   for `05`. If the existing notebook does not expose a needed diagnostic, treat
    its addition as a separately reviewed code change.
6. Commit sanitized aggregate outputs or an execution report under `docs/results/`.

   That directory is a proposed next artifact and is not present yet. Update this
    document's evidence status only after the run has actually completed.
