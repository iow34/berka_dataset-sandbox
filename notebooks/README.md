# Notebook workflow

Use the [setup guide](../docs/SETUP.md) first. Run with `notebooks/` as the working
directory so the existing `sys.path.append("..")` resolves `src/` correctly.
Restart the kernel between notebooks to release cached data and Spark sessions.

| Order | Notebook | Reads | Writes / result |
| --- | --- | --- | --- |
| 01 | [Load and clean](01_load_and_clean.ipynb) | Eight local source files | Appends to eight MySQL raw tables |
| 02 | [Build model](02_build_star_schema.ipynb) | MySQL raw tables | Appends to four dimensions, a bridge, and three facts |
| 03 | [Validate](03_validation.ipynb) | Raw and model tables | Displays eight raw counts and a 28-row quality report |
| 04 | [Investigate balances](04_investigation_balance_mismatch.ipynb) | `fact_transactions` | Displays diagnostic aggregates and sample-account reasoning |
| 05 | [Analyze client behavior](05_client_behavior_analysis.ipynb) | Model tables | Displays client profiles, segments, and loan-status comparisons |

Only `01` and `02` write database data. Neither is safe to rerun blindly against
populated tables: writes use append mode and existing primary keys reject repeats.
Notebooks `03`–`05` read the database; their derived DataFrames are not persisted.

## Source cleaning and model construction

`01` replaces exact `?` sentinels, renames and selects configured columns, and
casts types. Source dates remain strings in the raw layer. The loader expects
`district.csv`, whereas the upstream distribution calls it `district.asc`.

`02` generates a calendar from 1993-01-01 through 1998-12-31, decodes client birth
numbers, converts historical dates, and maps account-level records to facts.
The [data model guide](../docs/DATA_MODEL.md) defines each table's grain.

## Quality and investigation

`03` checks selected keys, fields, domains, balance arithmetic, and loan chronology.
It displays statuses; a `FAIL` does not automatically raise an exception or stop
execution. Inspect every result, including raw-table `MISMATCH` messages.

`04` compares naive transaction ordering with the implemented interest-first
ordering assumption. Earlier notes report fewer mismatches after the change,
with many remaining. Separate-batch processing and source rounding remain
explanations to investigate, not established facts about the original bank.
The investigation also contains a whole-unit-rounded exploratory check; it cannot
measure differences of 0.10. See [validation evidence](../docs/VALIDATION.md).

## Client analytics

`05` attributes transactions through `OWNER` links and derives RFM-style quartiles:
recency excluding `UROK`, frequency per active month, and signed net cash flow.
Excluding interest is a proxy for activity, not proof of client initiation. Other
automated postings can remain. Frequency and net flow still include interest.

Segment labels are exploratory rules. Loan-status percentages include clients
with no loans in the denominator and are not borrower default rates or predictive
performance. No statistical or causal conclusion is claimed.

## Execution evidence

All five notebooks currently have empty outputs. Narrative numbers from earlier
work are not a substitute for a saved run. For a shareable result, execute against
the intended local database, retain aggregate results, record environment versions
and the Git commit, and remove credentials or machine-specific diagnostics before
committing. The [validation guide](../docs/VALIDATION.md) lists the required evidence.
