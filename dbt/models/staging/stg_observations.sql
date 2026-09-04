select
    date as observation_date,
    indicator_id,
    value,
    loaded_at
from {{ source('raw', 'observations') }}