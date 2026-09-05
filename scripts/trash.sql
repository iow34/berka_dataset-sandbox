
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
from trans
limit 100;

SELECT COUNT(*) FROM trans;