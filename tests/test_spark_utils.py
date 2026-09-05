from src.spark_utils import clean_sentinels, cast_columns, rename_columns, prepare_table
from src.table_configs import rename_map, type_map

def test_clean_sentinels_replaces_question_mark_with_null(spark):
    df = spark.createDataFrame(
        [("77", "?"), ("1", "0.29")],
        ["district_id", "unemployment_rate_95"],
    )

    result = clean_sentinels(df)
    rows = {row.district_id: row.unemployment_rate_95 for row in result.collect()}

    assert rows["77"] is None
    assert rows["1"] == "0.29"

def test_clean_sentinels_does_not_change_other_text(spark):
    df = spark.createDataFrame([("OWNER",)], ["type"])
    result = clean_sentinels(df)
    assert result.collect()[0].type == "OWNER"    

def test_cast_colums_int_and_decimal(spark):
    df = spark.createDataFrame(
        [("77", "0.29")],
        ["district_id", "unemployment_rate_95"],
    )    

    result = cast_columns(
        df,
        {"district_id": "int", "unemployment_rate_95": "decimal(5,2)"}
    )
    row = result.collect()[0]

    assert row.district_id == 77
    assert str(row.unemployment_rate_95) == "0.29"
    assert dict(result.dtypes)["district_id"] == "int"
    assert dict(result.dtypes)["unemployment_rate_95"] == "decimal(5,2)"

def test_cast_columns_keep_null_after_sentinel(spark):
    df = spark.createDataFrame(
        [("77", "?")],
        ["district_id", "unemployment_rate_95"],
    )    
    cleaned = clean_sentinels(df)
    result = cast_columns(cleaned, {"unemployment_rate_95": "decimal(5,2)"})

    assert result.collect()[0].unemployment_rate_95 is None 

def test_rename_columns_changes_date_to_date_created(spark):
    df = spark.createDataFrame(
        [("1", "930101")],
        ["account_id", "date"],
    )
    result = rename_columns(df, {"date": "date_created", "account_id": "account_id"})

    assert "date_created" in result.columns
    assert "date" not in result.columns
    assert result.collect()[0].date_created == "930101"


def test_prepare_table_sentinel_rename_and_cast(spark):
    df = spark.createDataFrame(
        [("77", "?")],
        ["A1", "A12"],
    )
    result = prepare_table(
        df,
        {"A1": "district_id", "A12": "unemployment_rate_95"},
        {"district_id": "int", "unemployment_rate_95": "decimal(5,2)"},
    )
    row = result.collect()[0]

    assert result.columns == ["district_id", "unemployment_rate_95"]
    assert row.district_id == 77
    assert row.unemployment_rate_95 is None


def test_prepare_table_with_account_config(spark):
    df = spark.createDataFrame(
        [("1", "18", "POPLATEK MESICNE", "930101")],
        ["account_id", "district_id", "frequency", "date"],
    )
    result = prepare_table(df, rename_map("account"), type_map("account"))

    assert "date_created" in result.columns
    assert dict(result.dtypes)["account_id"] == "int"
    assert result.collect()[0].date_created == "930101"    