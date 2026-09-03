CREATE TABLE IF NOT EXISTS indicators (
    indicator_id SERIAL PRIMARY KEY,
    indicator_symbol TEXT NOT NULL,
    indicator_name TEXT NOT NULL,
    indicator_source TEXT NOT NULL,
    indicator_unit TEXT NOT NULL,
    category TEXT NOT NULL,
    frequency TEXT NOT NULL,
    UNIQUE (indicator_symbol, indicator_name)
);

CREATE TABLE IF NOT EXISTS observations (
    date DATE NOT NULL,
    indicator_id INT NOT NULL REFERENCES indicators(indicator_id),
    value NUMERIC(15, 4) NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY(date, indicator_id)
);
