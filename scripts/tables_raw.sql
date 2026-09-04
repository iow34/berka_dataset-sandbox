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
    unemployment_rate_95           DECIMAL(5,2)    NULL COMMENT 'В оригіналі іноді "?" для Praha — допускаємо NULL',
    unemployment_rate_96           DECIMAL(5,2)    NOT NULL,
    no_of_entrepreneurs_per_1000   INT             NOT NULL,
    no_of_crimes_95                INT             NULL COMMENT 'Той самий нюанс, що й unemployment_rate_95',
    no_of_crimes_96                INT             NOT NULL
);

CREATE TABLE client (
    client_id     INT PRIMARY KEY,
    birth_number  CHAR(6)  NOT NULL COMMENT 'YYMMDD; місяць+50 = жінка',
    district_id   INT      NOT NULL,
    FOREIGN KEY (district_id) REFERENCES district(district_id),
    INDEX idx_client_district (district_id)
);

CREATE TABLE account (
    account_id    INT PRIMARY KEY,
    district_id   INT          NOT NULL,
    frequency     VARCHAR(30)  NOT NULL,
    date_created  CHAR(6)      NOT NULL COMMENT 'YYMMDD, сире значення з джерела',
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
    issued   VARCHAR(15)  NOT NULL COMMENT 'YYMMDD HH:MM:SS, сире значення',
    FOREIGN KEY (disp_id) REFERENCES disp(disp_id)
);

CREATE TABLE loan (
    loan_id       INT PRIMARY KEY,
    account_id    INT            NOT NULL,
    date_granted  CHAR(6)        NOT NULL COMMENT 'YYMMDD',
    amount        DECIMAL(12,2)  NOT NULL,
    duration      INT            NOT NULL COMMENT 'у місяцях',
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
    k_symbol     VARCHAR(20)    NULL COMMENT 'буває відсутній у частини записів',
    FOREIGN KEY (account_id) REFERENCES account(account_id)
);

CREATE TABLE trans (
    trans_id     INT PRIMARY KEY,
    account_id   INT            NOT NULL,
    date_trans   CHAR(6)        NOT NULL COMMENT 'YYMMDD',
    type         VARCHAR(20)    NOT NULL COMMENT 'PRIJEM / VYDAJ',
    operation    VARCHAR(30)    NULL COMMENT 'буває порожнім для деяких типів транзакцій',
    amount       DECIMAL(12,2)  NOT NULL,
    balance      DECIMAL(12,2)  NOT NULL,
    k_symbol     VARCHAR(30)    NULL COMMENT 'порожній рядок у джерелі -> NULL',
    bank         CHAR(2)        NULL COMMENT 'заповнено лише для операцій з іншим банком',
    account      VARCHAR(20)    NULL COMMENT 'заповнено лише разом з bank',
    FOREIGN KEY (account_id) REFERENCES account(account_id),
    INDEX idx_trans_account_date (account_id, date_trans)
);