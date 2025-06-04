
-- Dim tables
CREATE TABLE IF NOT EXISTS dim_restaurants (
    restaurant_id       INT
    ,restaurant         TEXT
    ,restaurant_short   TEXT

    ,CONSTRAINT pk_dim_restaurants PRIMARY KEY(restaurant_id)
);

CREATE TABLE IF NOT EXISTS dim_meal_types (
    meal_type_id        INT     PRIMARY KEY
    ,meal_type          TEXT
    ,meal_type_en       TEXT
);

CREATE TABLE IF NOT EXISTS dim_meals (
    id              INT     PRIMARY KEY
    ,meal_codes     INT[]
    ,names          TEXT[]
    ,restaurants    INT[]
    ,meal_type      INT
    ,schoolyear     TEXT
    ,attributes     TEXT[]
    ,co2            FLOAT
    ,src            TEXT[]

    -- ,CONSTRAINT fk_dim_restaurants FOREIGN KEY(restaurants) REFERENCES dim_restaurants(restaurant_id)
    ,CONSTRAINT fk_dim_meal_types FOREIGN KEY(meal_type) REFERENCES dim_meal_types(meal_type_id)
);


-- Fact tables
CREATE TABLE IF NOT EXISTS menus (
    id                  TEXT    PRIMARY KEY
    ,weeklevel_idx      UUID    NOT NULL
    ,restaurant         INT     NOT NULL
    ,date               DATE    NOT NULL
    ,whole_pos          FLOAT   NOT NULL
    ,whole_waste        FLOAT   NOT NULL
    ,score              FLOAT   NOT NULL

    ,CONSTRAINT fk_dim_restaurants FOREIGN KEY(restaurant) REFERENCES dim_restaurants(restaurant_id)
);

CREATE TABLE IF NOT EXISTS meals_planned (
    menu_id TEXT
    ,meal   INT     NOT NULL
    ,pos    FLOAT   NOT NULL

    ,CONSTRAINT fk_menu FOREIGN KEY(menu_id) REFERENCES menus(id)
    ,CONSTRAINT fk_dim_meals FOREIGN KEY(meal) REFERENCES dim_meals(id)
);

