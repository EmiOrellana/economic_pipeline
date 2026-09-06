with expanded_observations as (
    select 
        o.observation_date as source_date,
        indicator_id,
        i.indicator_name,
        i.indicator_unit,
        i.category,
        i.frequency,
        g.grain,
        o.value,
        date_trunc(g.grain, o.observation_date)::date as period_start
    from {{ ref('stg_observations') }} as o
    join {{ ref('stg_indicators') }} as i using (indicator_id)
    cross join (values ('day'), ('month'), ('quarter'), ('year')) as g(grain)
    where 
        case g.grain
            when 'day' then 1
            when 'month' then 2
            when 'quarter' then 3
            when 'year' then 4
        end
        >=
        case i.frequency
            when 'daily' then 1
            when 'business_daily' then 1
            when 'monthly' then 2
            when 'quarterly' then 3
        end
),
collapsed_observation as (
    select distinct on (indicator_id, grain, period_start) 
        indicator_id,
        indicator_name,
        indicator_unit,
        category,
        frequency,
        grain,
        period_start as observation_date,
        value
    from expanded_observations
    order by indicator_id, grain, period_start, source_date desc
),
previous_observation as (
    select 
        *,
        lag(value, 1) over w as prev_period_value,
        case grain
            when 'month' then lag(value, 12) over w
            when 'quarter' then lag(value, 4) over w
            when 'year' then lag(value, 1) over w
    end as prev_year_value
    from collapsed_observation
    window w as (partition by indicator_id, grain order by observation_date)
)

select 
    indicator_id,
    indicator_name,
    indicator_unit,
    category,
    frequency,
    grain,
    observation_date,
    value,
    value - prev_period_value as pop_change,
    (value - prev_period_value) / nullif(prev_period_value, 0) * 100 as pop_pct,
    value - prev_year_value as yoy_change,
    (value - prev_year_value) / nullif(prev_year_value, 0) * 100 as yoy_pct
from previous_observation
