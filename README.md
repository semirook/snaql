# Snaql. Raw SQL queries from Python without pain [![Build Status](https://travis-ci.org/semirook/snaql.png)](https://travis-ci.org/semirook/snaql)

Totally inspired by [Yesql](https://github.com/krisajenkins/yesql) from Clojure world. 
But implemented in another way.

## What?

I totally agree with Yesql's author that SQL is already a mature DSL and great abstaction layer 
for DB queries building. And we don't need another layer above SQL to work with RDBMS like ORMs 
or complicated DSLs. Feel free to use all of the SQL's power in your projects without mixing Python 
code and SQL strings. Solution is very simple and flexible enough to try it in your next project. 
Also, Snaql doesn't depend on DB clients, can be used in asynchronous handlers (Tornado, for example). 
It's just a way to organize your queries and a bit of logic to change them with extra-context. Look at examples.

## Installation

As usual, with pip:

```bash
$ pip install snaql
```

## Examples

Create some folder and related namespace-files with your future SQL-queries. 
Like this, for example:

```
/queries
    users.sql
```

Prepare some SQL inside ```users.sql``` using block ```sql``` 
(Snaql is based on Jinja2 template engine and you can use it features):

```
{% sql 'users_by_country', note='counts users' %}
    SELECT count(*) AS count
    FROM user
    WHERE country_code = ?
{% endsql %}
```

Yes, that's it. SQL is inside ```sql``` block and ```note``` is 
optional, it's docstring for dynamically created function-generator
with name 'users_by_country' in this case.

What's next?

Import factory ```Snaql```:

```python
from snaql.factory import Snaql
```

Register SQL folder location:

```python
root_location = os.path.abspath(os.path.dirname(__file__))
snaql_factory = Snaql(root_location, 'queries')
```

```queries``` is a folder with SQL templates inside your root location. 

Register SQL template file with queries:

```python
users_queries = snaql_factory.load_queries('users.sql')
```

Get rendered SQL by it's meta-name:

```python
your_sql = users_queries.users_by_country()

# SELECT count(*) AS count
# FROM user
# WHERE country_code = ?
```

Cool! No?.. Hm, maybe you need some more flexibility? Remember, SQL templates 
are Jinja-powered and you can render them with some context. Example:

```
# users.sql, you can add as many sql blocks in a single file as you need

{% sql 'users_select_cond', note='select users with condition' %}
    SELECT *
    FROM user
    {% if users_ids %}
        WHERE user_id IN ({{ users_ids|join(', ') }})
    {% endif %}
{% endsql %}
```

Get it without context:

```python
your_sql = users_queries.users_select_cond()

# SELECT *
# FROM user 
```

And with context:

```python
sql_context = {'users_ids': [1, 2, 3]}
your_sql = users_queries.users_select_cond(**sql_context)

# SELECT *
# FROM user 
# WHERE user_id IN (1, 2, 3)
```

## Guards

Provides simple template variables guards to check or convert values to specific type.

**Guard name**        | **Description**                                                  |
----------------------|------------------------------------------------------------------|
guards.integer        | If value is string, tries to convert it to int()                 |
guards.float          | If value is string, tries to convert it to float()               |
guards.datetime       | Converts datetime object to formatted string YYYY-MM-DD HH:MI:SS |
guards.date           | Converts date object to formatted string YYYY-MM-DD              |
guards.time           | Converts time object to formatted string HH:MI:SS                |
guards.case           | Checks if value is in the case list                              |


Technically they are custom Jinja filters and can be used as usual.

```
{% sql 'select_by_id' %}
    SELECT *
    FROM news
    WHERE id = {{ news_id|guards.integer }}
{% endsql %}
```

```
{% sql 'get_news', note='get news by conditions' %}
    SELECT *
    FROM news
    {% if sort_order %}
        ORDER BY creation_date {{ sort_order|guards.case(['ASC', 'DESC']) }}
    {% endif %}
{% endsql %}
```

Each guard produces ```SnaqlGuardException``` if something goes wrong.

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

```
{% sql 'get_countries_by_conds', note='get countries by date conditions or ids' %}
    SELECT *
    FROM countries
    {% if ids %}
        WHERE id IN ({{ ids|join(', ') }})
    {% endif %}
    {% if date_from %}
        {% if ids %} AND {% endif %} WHERE creation_date >= {{ date_from }}
    {% endif %}
    {% if date_to %}
        {% if ids or date_from %} AND {% endif %} WHERE creation_date <= {{ date_to }}
    {% endif %}
    ORDER BY creation_date ASC
{% endsql %}
```

```python
def get_countries(ids=None, date_from=None, date_to=None):
    sql_context = {}
    if ids:
        sql_context['ids'] = ids
    if date_from:
        sql_context['date_from'] = date_from  # + date format 'YYYY-MM-DD'
    if date_to:
        sql_context['date_to'] = date_to  # + date format 'YYYY-MM-DD'

    return country_queries.get_countries_by_conds(**sql_context)
```

It's very error-prone, due to we need to check every variable presence and different
flow combinations. Imagine we have more complicated subquiries building! There is another 
way to organize SQL blocks here. Separate conditions blocks.

```
{% sql 'get_countries', note='get countries' %}
    SELECT *
    FROM countries
    {% if conditions %}
        {{ conditions|join(' AND ') }}
    {% endif %}
    ORDER BY creation_date ASC
{% endsql %}
```

```
{% sql 'cond_ids_in_countries' %}
    {% if ids %}
        WHERE id IN ({{ ids|join(', ') }})
    {% endif %}
{% endsql %}
```

```
{% sql 'cond_date_from_countries' %}
    {% if date_from %}
        WHERE creation_date >= {{ date_from }}
    {% endif %}
{% endsql %}
```

```
{% sql 'cond_date_to_countries' %}
    {% if date_to %}
        WHERE creation_date <= {{ date_to }}
    {% endif %}
{% endsql %}
```

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

    return country_queries.get_countries(conditions=sql_conditions)
```

It's more clear now. But not enough. Snaql provides tiny helper to 
organize your conditions related to the base query. Let's rewrite our example once again.

```
{% sql 'get_countries', note='get countries' %}
    SELECT *
    FROM countries
    {% if conditions %}
        {{ conditions|join(' AND ') }}
    {% endif %}
    ORDER BY creation_date ASC
{% endsql %}
```

Nothing changed here. But mark conditions with special ```cond_for``` parameter.

```
{% sql 'cond_ids_in_countries', cond_for='get_countries' %}
    {% if ids %}
        WHERE id IN ({{ ids|join(', ') }})
    {% endif %}
{% endsql %}
```

```
{% sql 'cond_date_from_countries', cond_for='get_countries' %}
    {% if date_from %}
        WHERE creation_date >= {{ date_from|guards.date }}
    {% endif %}
{% endsql %}
```

```
{% sql 'cond_date_to_countries', cond_for='get_countries' %}
    {% if date_to %}
        WHERE creation_date <= {{ date_to|guards.date }}
    {% endif %}
{% endsql %}
```

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
    # with relations checks and escapes final result
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
    # AND WHERE creation_date >= \\'2015-09-17\\'
    # ORDER BY creation_date ASC
```

Simple, without DB clients dependencies (use what you need). Try!
