import pytest  
from pyspark.sql import SparkSession

@pytest.fixture(scope="session")
def spark():
    session = (
        SparkSession.builder
        .appName("berka-tests")
        .master("local[1]")
        .getOrCreate()
    )
    yield session
    session.stop()