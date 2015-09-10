{% sql 'users_by_country', note='counts users' %}
    SELECT count(*) AS count
    FROM user
    WHERE country_code = ?
{% endsql %}

{% sql 'select_all' %}
    SELECT *
    FROM user
{% endsql %}

{% sql 'users_count_cond', note='counts users by country' %}
    SELECT count(*) AS count
    FROM user
    {% if by_country %}
        WHERE country_code = {{ country_code }}
    {% endif %}
{% endsql %}


{% sql 'users_select_cond', note='select users with condition' %}
    SELECT *
    FROM user
    {% if users_ids %}
        WHERE user_id IN ({{ users_ids|join(', ') }})
    {% endif %}
{% endsql %}


{% sql 'users_escaping', note='try to escape' %}
    SELECT *
    FROM user
    {% if user_name %}
        WHERE user_name = {{ user_name }}
    {% endif %}
{% endsql %}
