LOAD_ORDER = [
    "district",
    "client",
    "account",
    "disp",
    "card",
    "loan",
    "order",
    "trans",
]

TABLES = {
    "district": {
        "file": "district.csv",
        "db_table": "district",
        "columns": [
            ("A1", "district_id", "int"),
            ("A2", "district_name", "string"),
            ("A3", "region", "string"),
            ("A4", "no_of_inhabitants", "int"),
            ("A5", "no_of_municipalities_lt_499", "int"),
            ("A6", "no_of_municipalities_500_1999", "int"),
            ("A7", "no_of_municipalities_2000_9999", "int"),
            ("A8", "no_of_municipalities_gt_10000", "int"),
            ("A9", "no_of_cities", "int"),
            ("A10", "ratio_urban_inhabitants", "decimal(5,2)"),
            ("A11", "average_salary", "int"),
            ("A12", "unemployment_rate_95", "decimal(5,2)"),
            ("A13", "unemployment_rate_96", "decimal(5,2)"),
            ("A14", "no_of_entrepreneurs_per_1000", "int"),
            ("A15", "no_of_crimes_95", "int"),
            ("A16", "no_of_crimes_96", "int"),
        ],
    },
    "client": {
        "file": "client.asc",
        "db_table": "client",
        "columns": [
            ("client_id", "client_id", "int"),
            ("birth_number", "birth_number", "string"),
            ("district_id", "district_id", "int"),
        ],
    },
    "account": {
        "file": "account.asc",
        "db_table": "account",
        "columns": [
            ("account_id", "account_id", "int"),
            ("district_id", "district_id", "int"),
            ("frequency", "frequency", "string"),
            ("date", "date_created", "string"),
        ],
    },
    "disp": {
        "file": "disp.asc",
        "db_table": "disp",
        "columns": [
            ("disp_id", "disp_id", "int"),
            ("client_id", "client_id", "int"),
            ("account_id", "account_id", "int"),
            ("type", "type", "string"),
        ],
    },
    "card": {
        "file": "card.asc",
        "db_table": "card",
        "columns": [
            ("card_id", "card_id", "int"),
            ("disp_id", "disp_id", "int"),
            ("type", "type", "string"),
            ("issued", "issued", "string"),
        ],
    },
    "loan": {
        "file": "loan.asc",
        "db_table": "loan",
        "columns": [
            ("loan_id", "loan_id", "int"),
            ("account_id", "account_id", "int"),
            ("date", "date_granted", "string"),
            ("amount", "amount", "decimal(12,2)"),
            ("duration", "duration", "int"),
            ("payments", "payments", "decimal(10,2)"),
            ("status", "status", "string"),
        ],
    },
    "order": {
        "file": "order.asc",
        "db_table": "`order`",
        "columns": [
            ("order_id", "order_id", "int"),
            ("account_id", "account_id", "int"),
            ("bank_to", "bank_to", "string"),
            ("account_to", "account_to", "string"),
            ("amount", "amount", "decimal(12,2)"),
            ("k_symbol", "k_symbol", "string"),
        ],
    },
    "trans": {
        "file": "trans.asc",
        "db_table": "trans",
        "columns": [
            ("trans_id", "trans_id", "int"),
            ("account_id", "account_id", "int"),
            ("date", "date_trans", "string"),
            ("type", "type", "string"),
            ("operation", "operation", "string"),
            ("amount", "amount", "decimal(12,2)"),
            ("balance", "balance", "decimal(12,2)"),
            ("k_symbol", "k_symbol", "string"),
            ("bank", "bank", "string"),
            ("account", "account", "string"),
        ],
    },
}


def rename_map(table_key: str) -> dict[str, str]:
    return {csv: db for csv, db, _ in TABLES[table_key]["columns"]}


def type_map(table_key: str) -> dict[str, str]:
    return {db: spark_type for _, db, spark_type in TABLES[table_key]["columns"]}