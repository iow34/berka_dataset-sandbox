# Case study: banking data modeling and quality investigation

## Problem and scope

Banking source tables contain transactions, accounts, clients, dispositions,
loans, cards, orders, and district attributes. These tables need consistent types,
clear analytical grains, and quality checks before they can support reporting.

This project uses the historical Berka / PKDD'99 dataset to demonstrate  
that workflow. It is not paid client work or a production banking system. The  
project contribution is the ingestion configuration, SQL model, transformations,  
validation functions, investigation, tests, and explanatory notebooks; the source  
dataset is attributed separately.

## Implementation

1. Defined source-to-target mappings and a foreign-key-safe loading order for

   eight files. PySpark replaces missing-value sentinels and applies explicit types.
2. Created a MySQL raw layer and an analytical model with four dimensions, a bridge,

   and three facts. The model separates transaction, loan, and standing-order grains.
3. Added checks for raw counts, selected foreign keys, unique keys, required values,

   domains, cumulative balances, and account/loan chronology.
4. Investigated a failed balance check using running totals, adjacent balances,

   daily aggregates, and a documented sample-account reconstruction.
5. Built owner-attributed client profiles and exploratory RFM-style segments,

   including a recency proxy that excludes interest postings.

Inspect the [notebook workflow](../notebooks/README.md) for the implementation and
[validation evidence](VALIDATION.md) for the distinction between code, prior notes,
and current verification.

## Balance investigation: result and limits

Earlier project notes report **865,166** mismatches with `(date_key, trans_id)`
ordering and **795,450** with interest (`UROK`) placed first within the day.
That is **69,716 fewer mismatches**, about **8.1% of the original mismatch count**;
roughly **75.3% of all 1,056,320 transaction rows** would still mismatch. These are
historical reported counts, not newly reproduced results; the notebooks contain
no saved outputs and the review could not connect to the local MySQL service.

The sample account `1033` documents a same-day interest posting and deposit whose
stated balances fit interest-first ordering more closely. Separate ID ranges are
consistent with different posting sequences, but do not prove the original
system's batch schedule. Differences of around 0.10 suggest a precision or posting
convention worth investigating; they do not establish the source-system cause.

A cumulative mismatch count is not a count of independently erroneous records.
One early difference can affect every later row for an account. The implementation
retains its 0.01 tolerance and the failure remains visible. More evidence is needed
to establish a general ordering rule and explain residual differences.

## Client analytics: what the segments mean

The exploratory score uses recency without `UROK`, average transactions per active
month, and net cash flow. Frequency and monetary values still include all postings.
Quartile scores are summed into `Champions`, `Loyal`, `At Risk`, and `Lost` labels.
These are heuristic names, not validated customer states or risk predictions.

Excluding interest does not exclude every automated posting. Clients without a
qualifying posting can have NULL recency. Quartile ties have no explicit secondary
key, so segment membership can vary for equal values. The loan comparison counts
clients without loans in the denominator; it cannot be read as borrower default
probability. Earlier percentage claims are omitted until a reproducible aggregate
report with explicit denominators is retained.

## Value demonstrated

The repository lets a reviewer inspect how source quirks become explicit mappings,
how analytical grains are defined, and how unexpected validation results are
investigated without hiding failure. It demonstrates practical PySpark, SQL, data
modeling, and data-quality reasoning. No revenue gain, runtime improvement, or
business KPI uplift was measured, so none is claimed.

## Next evidence to add

Retain a dated run of the quality report and investigation aggregates; record the
source revision, code commit, and environment; then add targeted tests for model,
validation, and analytics edge cases. These are follow-up work, not completed
features. The current unit-test result and source counts are recorded in
[VALIDATION.md](VALIDATION.md).
