{{ config(severity='warn') }}

select
    i.indicator_id,
    i.indicator_symbol,
    i.indicator_name,
    i.frequency,
    max(o.observation_date) as last_observation_date,
    current_date - max(o.observation_date) as days_since_last_observation
from {{ ref('stg_indicators') }} i
join {{ ref('stg_observations') }} o using (indicator_id)
group by i.indicator_id, i.indicator_symbol, i.indicator_name, i.frequency
having current_date - max(o.observation_date) >
    case i.frequency
        when 'daily' then 4
        when 'business_daily' then 7
        when 'monthly' then 80
        when 'quarterly' then 220
    end