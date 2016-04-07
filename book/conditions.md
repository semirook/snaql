## Conditions

Often we need to create some dynamical set of query conditions. Look at the example,
that's how you usually build your final query with SQLAlchemy.

```python
def get_countries(ids=None, date_from=None, date_to=None):
    query = Country.query.order_by(Country.creation_date)
    if ids:
        query = query.filter(Country.id.in_(ids))
    if date_from:
        query = query.filter(Country.creation_date >= date_from)
    if date_to:
        query = query.filter(Country.creation_date <= date_to)
    return query.all()
```

To describe this logic in Snaql way we need to provide too verbose template.

{% raw %}
```
{% sql 'get_countries_by_conds', note='get countries by date conditions or ids' %}
    SELECT *
    FROM countries
    {% if ids %}
        WHERE id IN ({{ ids|join(', ') }})
    {% endif %}
    {% if date_from %}
        {% if ids %} AND {% endif %} creation_date >= {{ date_from }}
    {% endif %}
    {% if date_to %}
        {% if ids or date_from %} AND {% endif %} creation_date <= {{ date_to }}
    {% endif %}
    ORDER BY creation_date ASC
{% endsql %}
```
{% endraw %}

```python
def get_countries(ids=None, date_from=None, date_to=None):
    sql_context = {}
    if ids:
        sql_context['ids'] = ids
    if date_from:
        sql_context['date_from'] = date_from  # + date format 'YYYY-MM-DD'
    if date_to:
        sql_context['date_to'] = date_to  # + date format 'YYYY-MM-DD'

    country_queries = snaql_factory.load_queries('country.sql')

    return country_queries.get_countries_by_conds(**sql_context)
```

It's very error-prone, due to we need to check every variable presence and different
flow combinations. Imagine we have more complicated subquiries building! There is another 
way to organize SQL blocks here. Separate conditions blocks.

{% raw %}
```
{% sql 'get_countries', note='get countries' %}
    SELECT *
    FROM countries
    {% if conditions %}
        WHERE {{ conditions|join(' AND ') }}
    {% endif %}
    ORDER BY creation_date ASC
{% endsql %}
```
{% endraw %}

{% raw %}
```
{% sql 'cond_ids_in_countries' %}
    {% if ids %}
        id IN ({{ ids|join(', ') }})
    {% endif %}
{% endsql %}
```
{% endraw %}

{% raw %}
```
{% sql 'cond_date_from_countries' %}
    {% if date_from %}
        creation_date >= {{ date_from }}
    {% endif %}
{% endsql %}
```
{% endraw %}

{% raw %}
```
{% sql 'cond_date_to_countries' %}
    {% if date_to %}
        creation_date <= {{ date_to }}
    {% endif %}
{% endsql %}
```
{% endraw %}

```python
def get_countries(ids=None, date_from=None, date_to=None):
    sql_conditions = []
    if ids:
        cond = country_queries.cond_ids_in_countries(ids=ids)
        sql_conditions.append(cond)
    if date_from:
        cond = country_queries.cond_date_from_countries(date_from=date_from)
        sql_conditions.append(cond)
    if date_to:
        cond = country_queries.cond_date_to_countries(date_to=date_to)
        sql_conditions.append(cond)

    country_queries = snaql_factory.load_queries('country.sql')

    return country_queries.get_countries(conditions=sql_conditions)
```

It's more clear now. But not enough. Snaql provides tiny helper to 
organize your conditions related to the base query. Let's rewrite our example once again.

{% raw %}
```
{% sql 'get_countries', note='get countries' %}
    SELECT *
    FROM countries
    {% if conditions %}
        WHERE {{ conditions|join(' AND ') }}
    {% endif %}
    ORDER BY creation_date ASC
{% endsql %}
```
{% endraw %}

Nothing changed here. But mark conditions with special ```cond_for``` parameter.

{% raw %}
```
{% sql 'cond_ids_in_countries', cond_for='get_countries' %}
    {% if ids %}
        id IN ({{ ids|join(', ') }})
    {% endif %}
{% endsql %}
```
{% endraw %}

{% raw %}
```
{% sql 'cond_date_from_countries', cond_for='get_countries' %}
    {% if date_from %}
        creation_date >= {{ date_from|guards.date }}
    {% endif %}
{% endsql %}
```
{% endraw %}

{% raw %}
```
{% sql 'cond_date_to_countries', cond_for='get_countries' %}
    {% if date_to %}
        creation_date <= {{ date_to|guards.date }}
    {% endif %}
{% endsql %}
```
{% endraw %}

All ```cond_for``` blocks are related to ```get_countries``` query only.
Snaql checks that and doesn't allow you to use foreign conditions.
Also, you can't render condition block individually, it has no sense. Both 
situations will raise ```SnaqlException```. Now, you code may look like this:

```python
def get_countries(ids=None, date_from=None, date_to=None):
    sql_context = {}
    if ids:
        sql_context['ids'] = ids

    # guard will format date objects automatically
    if date_from:
        sql_context['date_from'] = date_from
    if date_to:
        sql_context['date_to'] = date_to

    # note, you don't call conditions functions explicitly,
    # Snaql will do that during main block rendering
    # with relations checks

    country_queries = snaql_factory.load_queries('country.sql')
    return country_queries.get_countries_by_conds(
        conditions=[
            country_queries.cond_ids_in_countries,
            country_queries.cond_date_from_countries,
            country_queries.cond_date_to_countries,
        ], **sql_context
    )

    # If ids are [1, 2, 3] and date_from is current date obj
    # and date_to is None, you'll get something like this:
    # 
    # SELECT * FROM news WHERE id IN (1, 2, 3) 
    # AND creation_date >= '2015-09-17'
    # ORDER BY creation_date ASC
```
