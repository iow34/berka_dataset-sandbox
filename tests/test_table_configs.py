from src.table_configs import LOAD_ORDER, TABLES, rename_map, type_map


def test_load_order_matches_tables():
    assert set(LOAD_ORDER) == set(TABLES)
    assert LOAD_ORDER[0] == "district"


def test_district_rename_and_types():
    assert rename_map("district")["A12"] == "unemployment_rate_95"
    assert type_map("district")["unemployment_rate_95"] == "decimal(5,2)"


def test_every_table_has_file_and_triples():
    for key, cfg in TABLES.items():
        assert "file" in cfg and "db_table" in cfg and "columns" in cfg
        assert cfg["columns"], key
        for triple in cfg["columns"]:
            assert len(triple) == 3, key