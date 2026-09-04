SELECT COUNT(*) AS total,
       SUM(bank IS NULL) AS bank_nulls,
       SUM(k_symbol = '' OR k_symbol IS NULL) AS empty_symbol
FROM trans;


select *
from trans
limit 100;

SELECT COUNT(*) FROM district;