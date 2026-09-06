
-- SET FOREIGN_KEY_CHECKS = 0;
-- TRUNCATE TABLE fact_transactions;
-- TRUNCATE TABLE fact_loans;
-- TRUNCATE TABLE fact_orders;
-- TRUNCATE TABLE bridge_client_account;
-- TRUNCATE TABLE dim_account;
-- TRUNCATE TABLE dim_client;
-- TRUNCATE TABLE dim_district;
-- TRUNCATE TABLE dim_date;
-- SET FOREIGN_KEY_CHECKS = 1;


USE bank_sandbox;

-- ============ DIMS ============

CREATE TABLE dim_date (
    date_key      INT PRIMARY KEY COMMENT 'YYYYMMDD',
    full_date     DATE NOT NULL,
    year          SMALLINT NOT NULL,
    quarter       TINYINT NOT NULL,
    month         TINYINT NOT NULL,
    month_name    VARCHAR(15) NOT NULL,
    day           TINYINT NOT NULL,
    day_of_week   TINYINT NOT NULL COMMENT '1=Sunday ... 7=Saturday',
    day_name      VARCHAR(15) NOT NULL,
    is_weekend    TINYINT(1) NOT NULL,
    
    INDEX idx_dim_date_full (full_date)
);

CREATE TABLE dim_district (
    district_id                    INT PRIMARY KEY,
    district_name                  VARCHAR(100) NOT NULL,
    region                         VARCHAR(100) NOT NULL,
    no_of_inhabitants              INT NOT NULL,
    no_of_municipalities_lt_499    INT NOT NULL,
    no_of_municipalities_500_1999  INT NOT NULL,
    no_of_municipalities_2000_9999 INT NOT NULL,
    no_of_municipalities_gt_10000  INT NOT NULL,
    no_of_cities                   INT NOT NULL,
    ratio_urban_inhabitants        DECIMAL(5,2) NOT NULL,
    average_salary                 INT NOT NULL,
    unemployment_rate_95           DECIMAL(5,2) NULL,
    unemployment_rate_96           DECIMAL(5,2) NOT NULL,
    no_of_entrepreneurs_per_1000   INT NOT NULL,
    no_of_crimes_95                INT NULL,
    no_of_crimes_96                INT NOT NULL
);

CREATE TABLE dim_client (
    client_id    INT PRIMARY KEY,
    district_id  INT NOT NULL,
    birth_date   DATE NOT NULL,
    gender       CHAR(1) NOT NULL COMMENT 'M/F, розкодовано з birth_number',
    
    FOREIGN KEY (district_id) REFERENCES dim_district(district_id),
    
    INDEX idx_dim_client_district (district_id)
);

CREATE TABLE dim_account (
    account_id   INT PRIMARY KEY,
    district_id  INT NOT NULL,
    frequency    VARCHAR(30) NOT NULL,
    open_date    DATE NOT NULL,
    
    FOREIGN KEY (district_id) REFERENCES dim_district(district_id),
    
    INDEX idx_dim_account_district (district_id)
);

CREATE TABLE bridge_client_account (
    client_id         INT NOT NULL,
    account_id        INT NOT NULL,
    disposition_type  VARCHAR(20) NOT NULL COMMENT 'OWNER / DISPONENT',
    
    PRIMARY KEY (client_id, account_id),
    FOREIGN KEY (client_id)  REFERENCES dim_client(client_id),
    FOREIGN KEY (account_id) REFERENCES dim_account(account_id),
    
    INDEX idx_bridge_account (account_id)
);

-- ============ FACTS ============

CREATE TABLE fact_transactions (
    trans_id    INT PRIMARY KEY,
    account_id  INT NOT NULL,
    date_key    INT NOT NULL,
    type        VARCHAR(20) NOT NULL,
    operation   VARCHAR(30) NULL,
    k_symbol    VARCHAR(30) NULL,
    amount      DECIMAL(12,2) NOT NULL,
    balance     DECIMAL(12,2) NOT NULL,
    
    FOREIGN KEY (account_id) REFERENCES dim_account(account_id),
    FOREIGN KEY (date_key)   REFERENCES dim_date(date_key),
    
    INDEX idx_fact_trans_account_date (account_id, date_key)
);

CREATE TABLE fact_loans (
    loan_id     INT PRIMARY KEY,
    account_id  INT NOT NULL,
    date_key    INT NOT NULL,
    amount      DECIMAL(12,2) NOT NULL,
    duration    INT NOT NULL,
    payments    DECIMAL(10,2) NOT NULL,
    status      CHAR(1) NOT NULL,
    
    FOREIGN KEY (account_id) REFERENCES dim_account(account_id),
    FOREIGN KEY (date_key)   REFERENCES dim_date(date_key)
);

CREATE TABLE fact_orders (
    order_id    INT PRIMARY KEY,
    account_id  INT NOT NULL,
    bank_to     CHAR(2) NOT NULL,
    account_to  VARCHAR(20) NOT NULL,
    k_symbol    VARCHAR(20) NULL,
    amount      DECIMAL(12,2) NOT NULL,
    
    FOREIGN KEY (account_id) REFERENCES dim_account(account_id)
);





