
-- SET FOREIGN_KEY_CHECKS = 0;
-- TRUNCATE TABLE trans;
-- TRUNCATE TABLE `order`;
-- TRUNCATE TABLE loan;
-- TRUNCATE TABLE card;
-- TRUNCATE TABLE disp;
-- TRUNCATE TABLE account;
-- TRUNCATE TABLE client;
-- TRUNCATE TABLE district;
-- SET FOREIGN_KEY_CHECKS = 1;


SELECT COUNT(*) AS total,
       SUM(bank IS NULL) AS bank_nulls,
       SUM(k_symbol = '' OR k_symbol IS NULL) AS empty_symbol
FROM trans;


select *
from district
limit 100;

SELECT COUNT(*) FROM trans;

ALTER TABLE district 
    DROP COLUMN A13,
    DROP COLUMN A14,
    DROP COLUMN A15,
    DROP COLUMN A16;


SELECT 'dim_date' t, COUNT(*) c FROM dim_date
UNION ALL SELECT 'dim_district', COUNT(*) FROM dim_district
UNION ALL SELECT 'dim_client', COUNT(*) FROM dim_client
UNION ALL SELECT 'dim_account', COUNT(*) FROM dim_account
UNION ALL SELECT 'bridge_client_account', COUNT(*) FROM bridge_client_account
UNION ALL SELECT 'fact_transactions', COUNT(*) FROM fact_transactions
UNION ALL SELECT 'fact_loans', COUNT(*) FROM fact_loans
UNION ALL SELECT 'fact_orders', COUNT(*) FROM fact_orders;

-- Очікування: 
-- dim_client = 5369 (як і client), 
-- bridge_client_account = 5369 (як і disp), 
-- fact_transactions = 1 056 320, 
-- fact_loans = 682, 
-- fact_orders = 6471, 
-- dim_district = 77, 
-- dim_date = кількість днів між 1993-01-01 і 1998-12-31 (близько 2192).

