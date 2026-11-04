USE bank_sandbox;

CREATE TABLE district (
    district_id                    INT PRIMARY KEY,
    district_name                  VARCHAR(100)    NOT NULL,
    region                          VARCHAR(100)    NOT NULL,
    no_of_inhabitants              INT             NOT NULL,
    no_of_municipalities_lt_499    INT             NOT NULL,
    no_of_municipalities_500_1999  INT             NOT NULL,
    no_of_municipalities_2000_9999 INT             NOT NULL,
    no_of_municipalities_gt_10000  INT             NOT NULL,
    no_of_cities                   INT             NOT NULL,
    ratio_urban_inhabitants        DECIMAL(5,2)    NOT NULL,
    average_salary                 INT             NOT NULL,
    unemployment_rate_95           DECIMAL(5,2)    NULL COMMENT 'Source may contain a question-mark sentinel; stored as NULL',
    unemployment_rate_96           DECIMAL(5,2)    NOT NULL,
    no_of_entrepreneurs_per_1000   INT             NOT NULL,
    no_of_crimes_95                INT             NULL COMMENT 'Source may contain a question-mark sentinel; stored as NULL',
    no_of_crimes_96                INT             NOT NULL
);

CREATE TABLE client (
    client_id     INT PRIMARY KEY,
    birth_number  CHAR(6)  NOT NULL COMMENT 'YYMMDD; month + 50 encodes female clients',
    district_id   INT      NOT NULL,
    FOREIGN KEY (district_id) REFERENCES district(district_id),
    INDEX idx_client_district (district_id)
);

CREATE TABLE account (
    account_id    INT PRIMARY KEY,
    district_id   INT          NOT NULL,
    frequency     VARCHAR(30)  NOT NULL,
    date_created  CHAR(6)      NOT NULL COMMENT 'YYMMDD, preserved source value',
    FOREIGN KEY (district_id) REFERENCES district(district_id),
    INDEX idx_account_district (district_id)
);

CREATE TABLE disp (
    disp_id     INT PRIMARY KEY,
    client_id   INT          NOT NULL,
    account_id  INT          NOT NULL,
    type        VARCHAR(20)  NOT NULL COMMENT 'OWNER / DISPONENT',
    FOREIGN KEY (client_id)  REFERENCES client(client_id),
    FOREIGN KEY (account_id) REFERENCES account(account_id),
    INDEX idx_disp_account_type (account_id, type)
);

CREATE TABLE card (
    card_id  INT PRIMARY KEY,
    disp_id  INT          NOT NULL,
    type     VARCHAR(20)  NOT NULL,
    issued   VARCHAR(15)  NOT NULL COMMENT 'YYMMDD HH:MM:SS, preserved source value',
    FOREIGN KEY (disp_id) REFERENCES disp(disp_id)
);

CREATE TABLE loan (
    loan_id       INT PRIMARY KEY,
    account_id    INT            NOT NULL,
    date_granted  CHAR(6)        NOT NULL COMMENT 'YYMMDD',
    amount        DECIMAL(12,2)  NOT NULL,
    duration      INT            NOT NULL COMMENT 'Duration in months',
    payments      DECIMAL(10,2)  NOT NULL,
    status        CHAR(1)        NOT NULL COMMENT 'A/B/C/D',
    FOREIGN KEY (account_id) REFERENCES account(account_id)
);

CREATE TABLE `order` (
    order_id     INT PRIMARY KEY,
    account_id   INT            NOT NULL,
    bank_to      CHAR(2)        NOT NULL,
    account_to   VARCHAR(20)    NOT NULL,
    amount       DECIMAL(12,2)  NOT NULL,
    k_symbol     VARCHAR(20)    NULL COMMENT 'Optional; missing in some source records',
    FOREIGN KEY (account_id) REFERENCES account(account_id)
);

CREATE TABLE trans (
    trans_id     INT PRIMARY KEY,
    account_id   INT            NOT NULL,
    date_trans   CHAR(6)        NOT NULL COMMENT 'YYMMDD',
    type         VARCHAR(20)    NOT NULL COMMENT 'PRIJEM / VYDAJ / VYBER',
    operation    VARCHAR(30)    NULL COMMENT 'May be empty for some transaction types',
    amount       DECIMAL(12,2)  NOT NULL,
    balance      DECIMAL(12,2)  NOT NULL,
    k_symbol     VARCHAR(30)    NULL COMMENT 'Empty source field is loaded as NULL',
    bank         CHAR(2)        NULL COMMENT 'Counterparty bank, when present in the source',
    account      VARCHAR(20)    NULL COMMENT 'Counterparty account, when present in the source',
    FOREIGN KEY (account_id) REFERENCES account(account_id),
    INDEX idx_trans_account_date (account_id, date_trans)
);