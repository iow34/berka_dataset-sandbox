import os
from pyspark.sql import SparkSession, functions as F
from dotenv import load_dotenv, find_dotenv
from pathlib import Path


def load_config() -> dict:
    env_path = find_dotenv()
    if not env_path:
        raise ValueError("Can't find .env - run code from the root")
    load_dotenv(env_path)

    jdbc_jar = os.getenv("JDBC_JAR_PATH")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")

    missing = [
        name for name, value in [
            ("JDBC_JAR_PATH", jdbc_jar),
            ("DB_HOST", db_host),
            ("DB_PORT", db_port),
            ("DB_NAME", db_name),
            ("DB_USER", db_user),
            ("DB_PASSWORD", db_password),
        ]
        if not value 
    ]
    if missing:
        raise ValueError(f"In .env missing: {', '.join(missing)}")

    project_root = Path(env_path).parent
    return {
        "raw_dir": project_root / "berka-dataset-raw",
        "jdbc_jar": jdbc_jar,
        "jdbc_url": (
            f"jdbc:mysql://{db_host}:{db_port}/{db_name}"
            "?allowPublicKeyRetrieval=true&useSSL=false"
        ),
        "db_user": db_user,
        "db_password": db_password,
    }

def get_spark(jdbc_jar: str, app_name: str = "berka-clean-load") -> SparkSession:
    return (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")
        .config("spark.jars", jdbc_jar)
        .getOrCreate()
    )           

def read_raw_csv(spark, path):
    return (spark.read
            .option("header", "true")
            .option("delimiter", ";")
            .option("quote", "\"")
            .option("nullValue", "")     # непроставлене значення (bank;;) -> NULL
            .option("emptyValue", "")    # порожній рядок у лапках ("") -> теж NULL
            .csv(str(path))
    )

def clean_sentinels(df, sentinel="?"):
    for c in df.columns:
        df = df.withColumn(c, F.when(F.col(c) == sentinel, None).otherwise(F.col(c)))
    return df            

def cast_columns(df, type_map: dict[str, str]):
    for column_name, spark_type in type_map.items():
        df = df.withColumn(
            column_name,
            F.col(column_name).cast(spark_type),
        )
    return df 

def rename_columns(df, mapping: dict[str, str]):
    for old_name, new_name in mapping.items():
        df = df.withColumnRenamed(old_name, new_name)
    return df


def prepare_table(df, col_rename: dict[str, str], col_types: dict[str, str]):
    df = clean_sentinels(df)
    df = rename_columns(df, col_rename)
    df = df.select(*col_rename.values())
    return cast_columns(df, col_types)

def write_to_mysql(df, table_name, jdbc_url, db_user, db_password):
    (df.write
       .format("jdbc")
       .option("url", jdbc_url)
       .option("dbtable", table_name)
       .option("user", db_user)
       .option("password", db_password)
       .option("driver", "com.mysql.cj.jdbc.Driver")
       .option("batchsize", 10000)   
       .mode("append")
       .save())    

def read_from_mysql(spark, jdbc_url, db_user, db_password, dbtable):
    return (spark.read
            .format("jdbc")
            .option("url", jdbc_url)
            .option("dbtable", dbtable)
            .option("user", db_user)
            .option("password", db_password)
            .option("driver", "com.mysql.cj.jdbc.Driver")
            .load())