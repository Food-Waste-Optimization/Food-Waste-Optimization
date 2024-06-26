CREATE TABLE restaurants (
    id INTEGER UNIQUE PRIMARY KEY,
    name TEXT
);

CREATE TABLE biowaste (
    date DATE,
    restaurant_id INTEGER REFERENCES restaurants (id),
    biowaste_customer NUMERIC,  -- Asiakasbiojäte
    biowaste_coffee NUMERIC,    -- Kahvinporot
    biowaste_kitchen NUMERIC,   -- Muu biojäte, keittiö
    biowaste_hall NUMERIC,      -- Muu biojäte, sali
    PRIMARY KEY (date, restaurant_id)
);

CREATE TABLE customers_per_hour (
    date DATE,
    hour INTEGER,
    amount INTEGER,
    restaurant_id INTEGER REFERENCES restaurants (id),
    PRIMARY KEY (date, hour, restaurant_id)
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE dishes (
    id SERIAL PRIMARY KEY,
    name TEXT,
    carbon_footprint NUMERIC,
    category_id INTEGER REFERENCES categories (id)
);

CREATE TABLE sold_lunches (
    datetime TIMESTAMP,
    amount INTEGER,
    restaurant_id INTEGER REFERENCES restaurants (id),
    dish_id INTEGER REFERENCES dishes (id),
    PRIMARY KEY (datetime, restaurant_id, dish_id)
);

