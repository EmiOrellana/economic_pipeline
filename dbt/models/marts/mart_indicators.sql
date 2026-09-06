select
    indicator_id,
    i.indicator_name,
    i.indicator_unit,
    i.category,
    i.frequency,
    min(o.observation_date) as start_date,
    max(o.observation_date) as end_date,
    count(*) as observation_count
from {{ ref('stg_indicators') }} as i
join {{ ref('stg_observations') }} as o using (indicator_id)
group by indicator_id, i.indicator_name, i.indicator_unit, i.category, i.frequency