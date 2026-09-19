from pyspark.sql import functions as F
from pyspark.sql import Window


def check_referential_integrity(fact_df, fact_fk_col, dim_df, dim_pk_col, check_name):
    """
    Completeness check: verify that every foreign key value in `fact_df`
    has a matching primary key value in `dim_df`.

    Uses a "left_anti" join, which returns only rows from `fact_df` that
    have NO match in `dim_df` -- these are "orphan" rows referencing a
    dimension record that does not exist.
    """
    orphans = fact_df.join(
        dim_df.select(dim_df[dim_pk_col]),
        fact_df[fact_fk_col] == dim_df[dim_pk_col],
        "left_anti",
    )
    orphan_count = orphans.count()
    return {
        "check": check_name,
        "dimension": "Completeness",
        "status": "OK" if orphan_count == 0 else "FAIL",
        "details": f"{orphan_count} orphan row(s)" if orphan_count else "all foreign keys resolved",
    }


def check_uniqueness(df, key_cols, check_name):
    """
    Uniqueness check: verify that the given column(s) uniquely identify
    each row, with no duplicate combinations.
    """
    total = df.count()
    distinct = df.select(*key_cols).distinct().count()
    dup_count = total - distinct
    return {
        "check": check_name,
        "dimension": "Uniqueness",
        "status": "OK" if dup_count == 0 else "FAIL",
        "details": f"{dup_count} duplicate key(s)" if dup_count else "all values unique",
    }


def check_not_null(df, cols, table_label):
    """
    Completeness check: verify that none of the given columns contain NULL.
    Returns a LIST of result dicts (one per column), since each column
    is checked independently.
    """
    results = []
    for c in cols:
        null_count = df.filter(F.col(c).isNull()).count()
        results.append({
            "check": f"{table_label}.{c} NOT NULL",
            "dimension": "Completeness",
            "status": "OK" if null_count == 0 else "FAIL",
            "details": f"{null_count} NULL value(s)" if null_count else "no NULLs found",
        })
    return results


def check_allowed_values(df, col, allowed_values, check_name):
    """
    Validity check: verify that every value in `col` belongs to a known,
    business-approved set of values (its "domain"). A value can be
    non-NULL (passes Completeness) and still be invalid if it falls
    outside this domain.
    """
    invalid_count = df.filter(~F.col(col).isin(allowed_values)).count()
    return {
        "check": check_name,
        "dimension": "Validity",
        "status": "OK" if invalid_count == 0 else "FAIL",
        "details": f"{invalid_count} value(s) outside {allowed_values}" if invalid_count else "all values within allowed domain",
    }

def check_loan_after_account_open(fact_loans_df, dim_account_df, dim_date_df, check_name="loan date not before account opening"):
    """
    Consistency check: verify that a loan's date is never earlier than
    the date its account was opened -- a simple cross-table business
    logic sanity check.
    """
    joined = (fact_loans_df
        .join(dim_date_df.select("date_key", "full_date"), "date_key")
        .join(dim_account_df.select("account_id", "open_date"), "account_id"))

    violations = joined.filter(F.col("full_date") < F.col("open_date"))
    violation_count = violations.count()

    return {
        "check": check_name,
        "dimension": "Consistency",
        "status": "OK" if violation_count == 0 else "FAIL",
        "details": f"{violation_count} loan(s) dated before account opening" if violation_count else "chronology is consistent",
    }
    
def check_running_balance(fact_transactions_df, check_name="transaction running balance reconciliation"):
    signed_amount = F.when(F.col("type") == "PRIJEM", F.col("amount")).otherwise(-F.col("amount"))
    urok_first = F.when(F.col("k_symbol") == "UROK", F.lit(0)).otherwise(F.lit(1))

    w = Window.partitionBy("account_id").orderBy("date_key", urok_first, "trans_id")

    with_running = (fact_transactions_df
        .withColumn("signed_amount", signed_amount)
        .withColumn("computed_balance", F.sum("signed_amount").over(w)))

    mismatches = with_running.filter(
        F.abs(F.col("computed_balance") - F.col("balance")) > F.lit(0.01)
    )
    mismatch_count = mismatches.count()

    result = {
        "check": check_name,
        "dimension": "Accuracy",
        "status": "OK" if mismatch_count == 0 else "FAIL",
        "details": f"{mismatch_count} row(s) where computed balance != stated balance" if mismatch_count else "balances reconcile",
    }
    return result, mismatches 