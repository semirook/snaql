## Examples

Create some folder and related namespace-files with your future queries. Like this, for example:

```
/queries
    users.sql
```

Prepare some SQL queries inside ```users.sql``` using block ```sql``` 
(Snaql is based on Jinja2 template engine and you can use it features):

{% raw %}
```
{% sql 'users_by_country', note='counts users' %}
    SELECT count(*) AS count
    FROM user
    WHERE country_code = ?
{% endsql %}
```
{% endraw %}

Yes, that's it. Your SQL is inside ```sql``` block and ```note``` is 
an optional docstring for dynamically created function-generator
with name 'users_by_country' in this case. You can use {% raw %}```{% query %}{% endquery %}```{% endraw %}
block if your query is too far from SQL. It's just an alias and this block equals to previous.

{% raw %}
```
{% query 'users_by_country', note='counts users' %}
    SELECT count(*) AS count
    FROM user
    WHERE country_code = ?
{% endquery %}
```
{% endraw %}

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

Cool! No?.. Hm, maybe you need some more flexibility? Remember, query blocks
are Jinja-powered and you can render them with some context. Example:

{% raw %}
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
{% endraw %}

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
