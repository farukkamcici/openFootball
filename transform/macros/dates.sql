-- macros/dates.sql

{% macro to_date(col) -%}
    -- Cast various string/timestamp inputs safely to DATE
    CAST({{ col }} AS DATE)
{%- endmacro %}
