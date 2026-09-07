with grain as (
    select
        indicator_id,
        array_agg(distinct grain) as available_grains
    from {{ ref('mart_observations') }}
    group by indicator_id
)

select
    indicator_id,
    i.indicator_name,
    i.indicator_unit,
    i.category,
    i.frequency,
    min(o.observation_date) as start_date,
    max(o.observation_date) as end_date,
    count(*) as observation_count,
    g.available_grains
from {{ ref('stg_indicators') }} as i
join {{ ref('stg_observations') }} as o using (indicator_id)
join grain as g using (indicator_id)
group by indicator_id, i.indicator_name, i.indicator_unit, i.category, i.frequency, g.available_grains