## Guards

Provides simple template variables guards to check or convert values to specific type.

**Guard name**        | **Description**                                                  
----------------------|------------------------------------------------------------------
guards.string         | Escapes string variable and surrounds it with quotes             
guards.integer        | If value is string, tries to convert it to int()                 
guards.float          | If value is string, tries to convert it to float()               
guards.datetime       | Converts datetime object to formatted string YYYY-MM-DD HH:MI:SS 
guards.date           | Converts date object to formatted string YYYY-MM-DD              
guards.time           | Converts time object to formatted string HH:MI:SS                
guards.case           | Checks if value is in the case list                              
guards.regexp         | Checks if value matches regular expression                       
guards.bool           | Bool check, returns 1 or 0


Technically they are custom Jinja filters and can be used as usual.

{% raw %}
```
{% sql 'select_by_id' %}
    SELECT *
    FROM news
    WHERE id = {{ news_id|guards.integer }}
{% endsql %}
```
{% endraw %}

{% raw %}
```
{% sql 'get_news', note='get news by conditions' %}
    SELECT *
    FROM news
    {% if sort_order %}
        ORDER BY creation_date {{ sort_order|guards.case(['ASC', 'DESC']) }}
    {% endif %}
{% endsql %}
```
{% endraw %}

{% raw %}
```
{% sql 'select_by_slug' %}
    SELECT *
    FROM news
    WHERE slug = '{{ slug|guards.regexp("^[A-Za-z][A-Za-z0-9_]{7,15}") }}'
{% endsql %}
```
{% endraw %}

Each guard produces ```SnaqlGuardException``` if something goes wrong.
