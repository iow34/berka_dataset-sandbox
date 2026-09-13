from pyspark.sql import functions as F


def build_client_transaction_profile(fact_transactions, bridge, dim_date, disposition_type="OWNER"):
    """
    One row per client_id summarizing transaction activity, attributed via
    the account(s) where the client holds the given disposition_type
    (default "OWNER" -- the primary financial actor on the account).
    """
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