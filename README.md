# Snaql. Raw SQL queries from Python without pain

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

Simple, without DB clients dependencies (use what you need), works in Python 2 and 3. Try!
