{% sql 'select_by_id' %}
    SELECT *
    FROM news
    WHERE id = {{ news_id }}
    AND creation_date >= {{ date_from }}
    AND rating >= {{ rating }}
{% endsql %}

{% sql 'select_by_slug' %}
    SELECT *
    FROM news
    WHERE slug = {{ slug }}
{% endsql %}
