from pyspark.sql import functions as F


def build_client_transaction_profile(fact_transactions, bridge, dim_date, disposition_type="OWNER"):

    owner_links = (bridge
        .filter(F.col("disposition_type") == disposition_type)
        .select("client_id", "account_id"))

    txns_with_client = (fact_transactions
        .join(owner_links, "account_id")
        .join(dim_date.select("date_key", "full_date"), "date_key"))

    signed = txns_with_client.withColumn(
        "signed_amount",
        F.when(F.col("type") == "PRIJEM", F.col("amount")).otherwise(-F.col("amount"))
    )

    profile = (signed
        .groupBy("client_id")
        .agg(
            F.count("*").alias("total_transactions"),
            F.sum(F.when(F.col("type") == "PRIJEM", F.col("amount")).otherwise(0)).alias("total_inflow"),
            F.sum(F.when(F.col("type") != "PRIJEM", F.col("amount")).otherwise(0)).alias("total_outflow"),
            F.sum("signed_amount").alias("net_flow"),
            F.avg("amount").alias("avg_transaction_amount"),
            F.min("full_date").alias("first_transaction_date"),
            F.max("full_date").alias("last_transaction_date"),
        ))

    return profile

def add_behavioral_features(profile, snapshot_day):
    return (
        profile
        .withColumn(
            "recency_days",
            F.datediff(F.lit(snapshot_day), F.col("last_transaction_date"))
        )
        .withColumn(
            "active_days",
            F.datediff(F.col("last_transaction_date"), F.col("first_transaction_date")) + 1
        )
        .withColumn(
            "avg_transactions_per_month",
            F.col("total_transactions") / (F.col("active_days") / F.lit(30.44))
        )
    )

def add_client_initiated_recency(profile, fact_transactions, bridge, dim_date, snapshot_date, disposition_type="OWNER"):
    owner_links = (bridge
        .filter(F.col("disposition_type") == disposition_type)
        .select("client_id", "account_id"))

    client_initiated = (fact_transactions
        .filter((F.col("k_symbol") != "UROK") | F.col("k_symbol").isNull())
        .join(owner_links, "account_id")
        .join(dim_date.select("date_key", "full_date"), "date_key"))

    last_real_activity = (client_initiated
        .groupBy("client_id")
        .agg(F.max("full_date").alias("last_client_initiated_date")))

    return (profile
        .join(last_real_activity, "client_id", "left")
        .withColumn(
            "recency_days_real",
            F.datediff(F.lit(snapshot_date), F.col("last_client_initiated_date"))
        )
    )    

def build_loan_status_flags(fact_loans, bridge, disposition_type="OWNER"):
    owner_links = (bridge
        .filter(F.col("disposition_type") == disposition_type)
        .select("client_id", "account_id"))

    loans_with_client = fact_loans.join(owner_links, "account_id")

    return (loans_with_client
        .groupBy("client_id")
        .agg(
            F.count("*").alias("loan_count"),
            F.max(F.when(F.col("status").isin("B", "D"), 1).otherwise(0)).alias("has_problem_loan")
        )
    )    