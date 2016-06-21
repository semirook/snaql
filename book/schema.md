## Schema

Since 0.4, Snaql natively supports great [Schema](https://github.com/keleshev/schema) library for the
context validation and more values transformation flexibility.

{% raw %}
```
{% sql 'select_by_id' %}
    SELECT *
    FROM news
    WHERE id = {{ news_id }}
    AND creation_date >= {{ date_from }}
    AND rating >= {{ rating }}
{% endsql %}
```
{% endraw %}

```python
import datetime
from snaql.factory import Snaql
from schema import Schema, And, Use, SchemaError
from snaql.convertors import guard_date


root_location = os.path.abspath(os.path.dirname(__file__))
snaql_factory = Snaql(root_location, 'queries')


news_queries = snaql_factory.load_queries('unsafe_news.sql')
schema = Schema({
    'news_id': And(Use(int), lambda i: i > 0),
    'rating': And(Use(float), lambda r: r > 0),
    'date_from': And(Use(guard_date)),
})
context = {
    'news_id': '123',
    'date_from': datetime.datetime.utcnow(),
    'rating': 4.22,
}
sql = news_queries.select_by_id(schema=schema, **context)

# SELECT * FROM news 
# WHERE id = 123 
# AND creation_date >= '2016-06-21' 
# AND rating >= 4.22
```

Sure, you can use standard "guards", convertors or create your own.
