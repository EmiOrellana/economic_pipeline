{{ config(severity='warn') }}

-- Detects unit or scale changes at the source, not market volatility.
-- The largest genuine move on record is +319% (Henry Hub, Jan 2024), so a
-- 10x threshold can only be tripped by something a market cannot do.

with variations as (

    select
        i.indicator_name,
        o.observation_date,
        o.value,
        lag(o.value) over (
            partition by o.indicator_id
            order by o.observation_date
        ) as prev_value

    from {{ ref('stg_observations') }} o
    join {{ ref('stg_indicators') }} i using (indicator_id)

)

select
    indicator_name,
    observation_date,
    prev_value,
    value,
    abs(value - prev_value) / nullif(abs(prev_value), 0) as change_ratio

from variations

where prev_value is not null
    and abs(value - prev_value) / nullif(abs(prev_value), 0) > 10
