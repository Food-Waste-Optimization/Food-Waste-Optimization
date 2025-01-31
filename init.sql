
CREATE TABLE IF NOT EXISTS meals (
    meal_id         INT     PRIMARY KEY
    ,aliases        TEXT[]
    ,meal_type      TEXT
    ,restaurant     TEXT[]
    ,schoolyear     TEXT
    ,attributes     TEXT[]
);

-- CREATE TABLE IF NOT EXISTS pieces_per_dish (
--     meal_id     INT     NOT NULL
--     ,restaurant TEXT    not null
--     ,date       date    NOT NULL
--     ,pcs        float   not null

--     ,constraint pk_pieces_per_dish primary key (meal_id, date, restaurant)
-- );


CREATE TABLE IF NOT EXISTS pieces_whole (
    date        date    NOT NULL
    ,restaurant TEXT    NOT NULL
    ,pcs        float   not null

    ,constraint pk_pieces_whole primary key (date, restaurant)
);

CREATE TABLE IF NOT EXISTS biowaste (
    meal_id     INT     PRIMARY KEY
    ,waste      float   not null
);


CREATE TABLE IF NOT EXISTS co2 (
    meal_id     INT     PRIMARY KEY
    ,co2        float   not null
);

CREATE TABLE IF NOT EXISTS menu (
    date                    DATE    NOT NULL
    ,restaurant             TEXT    not null
    ,meal_ids               INT[]   NOT NULL
    -- ,total_co2              float   not null
    -- ,total_waste            float   not null
    -- ,total_pcs_from_dishes  float   not null
    -- ,co2_per_customer       float   not null
    -- ,waste_per_customer     float   not null
    ,fitness                float   not null
    ,index                  BIGINT

    -- ,constraint pk_menu primary key (date, restaurant)
);