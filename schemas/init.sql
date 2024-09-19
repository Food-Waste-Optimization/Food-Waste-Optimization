CREATE TABLE IF NOT EXISTS pieces_per_dish (
    id          SERIAL  PRIMARY KEY
    ,date       date    NOT NULL
    ,restaurant TEXT    NOT NULL
    ,category   TEXT    not null
    ,dish       TEXT    NOT NULL
    ,pcs        float   not null
);


CREATE TABLE IF NOT EXISTS pieces_whole (
    id          SERIAL  PRIMARY KEY
    ,date       date    NOT NULL
    ,restaurant TEXT    NOT NULL
    ,pcs        float   not null
);

CREATE TABLE IF NOT EXISTS biowaste (
    id          SERIAL  PRIMARY KEY
    ,dish       TEXT    NOT NULL
    ,waste      float   not null
);


CREATE TABLE IF NOT EXISTS co2 (
    id          SERIAL  PRIMARY KEY
    ,dish       TEXT    NOT NULL
    ,waste      float   not null
);

CREATE TABLE IF NOT EXISTS menu (
    id                      SERIAL  PRIMARY KEY
    ,date                   DATE    NOT NULL
    ,restaurant             TEXT    not null
    ,dish_1                 TEXT    NOT NULL
    ,dish_2                 TEXT    NOT NULL
    ,dish_3                 TEXT    NOT NULL
    ,dish_4                 TEXT    NOT NULL
    ,total_co2              float   not null
    ,total_waste            float   not null
    ,total_pcs_from_dishes  float   not null
    ,co2_per_customer       float   not null
    ,waste_per_customer     float   not null
    ,fitness                float   not null 
);