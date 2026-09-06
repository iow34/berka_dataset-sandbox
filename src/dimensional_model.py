from pyspark.sql import functions as F


def build_dim_date(spark, start_date: str, end_date: str):
    date_range = spark.sql(f"""
        SELECT explode(sequence(
            to_date('{start_date}'), to_date('{end_date}'), interval 1 day
        )) AS full_date
    """)

    return (date_range
        .withColumn("date_key", F.date_format("full_date", "yyyyMMdd").cast("int"))
        .withColumn("year", F.year("full_date"))
        .withColumn("quarter", F.quarter("full_date"))
        .withColumn("month", F.month("full_date"))
        .withColumn("month_name", F.date_format("full_date", "MMMM"))
        .withColumn("day", F.dayofmonth("full_date"))
        .withColumn("day_of_week", F.dayofweek("full_date"))
        .withColumn("day_name", F.date_format("full_date", "EEEE"))
        .withColumn("is_weekend", F.when(F.dayofweek("full_date").isin(1, 7), 1).otherwise(0))
        .select("date_key", "full_date", "year", "quarter", "month",
                "month_name", "day", "day_of_week", "day_name", "is_weekend")
    )


def parse_yymmdd_to_date(df, col_name: str, new_col_name: str):
    return df.withColumn(
        new_col_name,
        F.to_date(F.concat(F.lit("19"), F.col(col_name)), "yyyyMMdd"),
    )


def decode_birth_number(df):
    yy = F.substring("birth_number", 1, 2)
    mm_raw = F.substring("birth_number", 3, 2).cast("int")
    dd = F.substring("birth_number", 5, 2)

    gender = F.when(mm_raw > 12, F.lit("F")).otherwise(F.lit("M"))
    mm_real = F.when(mm_raw > 12, mm_raw - 50).otherwise(mm_raw)

    birth_date_str = F.concat(
        F.lit("19"), yy,
        F.lpad(mm_real.cast("string"), 2, "0"),
        dd,
    )

    return (df
        .withColumn("gender", gender)
        .withColumn("birth_date", F.to_date(birth_date_str, "yyyyMMdd"))
    )