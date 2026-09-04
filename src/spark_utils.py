import os
from pyspark.sql import SparkSession, functions as F
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

env_path = find_dotenv()              # знаходить .env, де б він не був — вгору по деревi папок
load_dotenv(env_path)

PROJECT_ROOT = Path(env_path).parent  # тека, де лежить .env == корінь проекту
RAW_DIR = PROJECT_ROOT / "berka-dataset-raw"

spark = (SparkSession.builder
         .appName("berka-clean-load")
         .master("local[*]")
         .config("spark.jars", os.getenv("JDBC_JAR_PATH"))
         .getOrCreate())

jdbc_url = (f"jdbc:mysql://{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/"
            f"{os.getenv('DB_NAME')}?allowPublicKeyRetrieval=true&useSSL=false")

def read_raw_csv(spark, path):
    return (spark.read
            .option("header", "true")
            .option("delimiter", ";")
            .option("quote", "\"")
            .option("nullValue", "")     # непроставлене значення (bank;;) -> NULL
            .option("emptyValue", "")    # порожній рядок у лапках ("") -> теж NULL
            .csv(path))

def clean_sentinels(df, sentinel="?"):
    for c in df.columns:
        df = df.withColumn(c, F.when(F.col(c) == sentinel, None).otherwise(F.col(c)))
    return df            

def write_to_mysql(df, table_name, jdbc_url, db_user, db_password):
    (df.write
       .format("jdbc")
       .option("url", jdbc_url)
       .option("dbtable", table_name)
       .option("user", db_user)
       .option("password", db_password)
       .option("driver", "com.mysql.cj.jdbc.Driver")
       .option("batchsize", 10000)   # для великого trans.csv — суттєво швидше за дефолт
       .mode("append")
       .save())    

district_raw   = read_raw_csv(spark, f"{RAW_DIR}/district.csv")
district_clean = clean_sentinels(district_raw)

district_cols = ["district_id","district_name","region","no_of_inhabitants",
                  "no_of_municipalities_lt_499","no_of_municipalities_500_1999",
                  "no_of_municipalities_2000_9999","no_of_municipalities_gt_10000",
                  "no_of_cities","ratio_urban_inhabitants","average_salary",
                  "unemployment_rate_95","unemployment_rate_96",
                  "no_of_entrepreneurs_per_1000","no_of_crimes_95","no_of_crimes_96"]

district_clean = district_clean.toDF(*district_cols)  # позиційне перейменування

int_cols = ["district_id","no_of_inhabitants","no_of_municipalities_lt_499",
            "no_of_municipalities_500_1999","no_of_municipalities_2000_9999",
            "no_of_municipalities_gt_10000","no_of_cities","average_salary",
            "no_of_entrepreneurs_per_1000","no_of_crimes_95","no_of_crimes_96"]
dec_cols = ["ratio_urban_inhabitants","unemployment_rate_95","unemployment_rate_96"]

for c in int_cols:
    district_clean = district_clean.withColumn(c, F.col(c).cast("int"))
for c in dec_cols:
    district_clean = district_clean.withColumn(c, F.col(c).cast("decimal(5,2)"))

write_to_mysql(district_clean, "district", jdbc_url,
               os.getenv("DB_USER"), os.getenv("DB_PASSWORD"))       