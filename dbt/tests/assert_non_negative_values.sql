{{ config(severity='error') }}

-- Series that cannot be negative by construction: rates over counts and
-- index levels. Oil, gas and policy rates are deliberately excluded --
-- WTI settled at -36.98 on 2020-04-20 and that value is correct.

select
    i.indicator_name,
    o.observation_date,
    o.value

from {{ ref('stg_observations') }} o
join {{ ref('stg_indicators') }} i using (indicator_id)

where i.indicator_symbol in ('{{ var('non_negative_symbols') | join("', '") }}')
    and o.value < 0
