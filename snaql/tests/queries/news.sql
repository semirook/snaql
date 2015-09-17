{% sql 'select_all' %}
    SELECT *
    FROM news
{% endsql %}

{% sql 'select_by_id' %}
    SELECT *
    FROM news
    WHERE id = {{ news_id|guards.integer }}
    AND WHERE creation_date >= {{ date_from|guards.datetime }}
    AND WHERE rating >= {{ rating|guards.float }}
{% endsql %}

{% sql 'get_news', note='get news by conditions' %}
    SELECT *
    FROM news
    {% if conditions %}
        {{ conditions|join(' AND ') }}
    {% endif %}
    {% if sort_order %}
        ORDER BY creation_date {{ sort_order|guards.case(['ASC', 'DESC']) }}
    {% endif %}
{% endsql %}

{% sql 'cond_ids_in_news', cond_for='get_news' %}
    {% if ids %}
        WHERE id IN ({{ ids|join(', ') }})
    {% endif %}
{% endsql %}

{% sql 'cond_date_from_news', cond_for='get_news' %}
    {% if date_from %}
        WHERE creation_date >= {{ date_from|guards.date }}
    {% endif %}
{% endsql %}

{% sql 'cond_date_to_news', cond_for='get_news' %}
    {% if date_to %}
        WHERE creation_date <= {{ date_to|guards.date }}
    {% endif %}
{% endsql %}

{% sql 'cond_date_to_another_news', cond_for='get_another_news' %}
    {% if date_to %}
        WHERE creation_date = {{ date_to|guards.date }}
    {% endif %}
{% endsql %}

{% sql 'select_by_slug' %}
    SELECT *
    FROM news
    WHERE slug = '{{ slug|guards.regexp("^[A-Za-z][A-Za-z0-9_]{7,15}") }}'
{% endsql %}
