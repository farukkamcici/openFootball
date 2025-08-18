{% macro non_negative(col) -%}
    -- Enforce non-negative numeric fields; NULL if bad
    case when {{ col }} < 0 then null else {{ col }} end
{%- endmacro %}

{% macro int_or_null(col) -%}
    try_cast({{ col }} as integer)
{%- endmacro %}

{% macro int_or_zero(col) -%}
    coalesce(TRY_CAST({{ col }} AS INTEGER), 0)
{%- endmacro %}

{% macro bigint_or_null(col) -%}
    try_cast({{ col }} as bigint)
{%- endmacro %}

{% macro decimal_or_null(col, p=18, s=2) -%}
    try_cast({{ col }} as decimal({{p}},{{s}}))
{%- endmacro %}

{% macro clean_string(col) -%}
    -- Trim + empty strings → NULL
    nullif(trim(cast({{ col }} AS varchar)), '')
{%- endmacro %}
