select
    indicator_id,
    indicator_symbol,
    indicator_name,
    indicator_source,
    indicator_unit,
    category,
    frequency
from {{ source('raw', 'indicators') }}