## Blocks order

There are cases when queries order matters. Like tables creation, for example.
And Snaql has solution to mark blocks dependencies with ```depends_on``` list.

{% raw %}
```
{% query 'create_nodes', depends_on=['create_templates', 'create_flavors'] %}
    CREATE TABLE nodes (
        id VARCHAR(50) NOT NULL, 
        type VARCHAR(6), 
        properties VARCHAR(1024), 
        template_id VARCHAR(36), 
        flavor_id VARCHAR(36), 
        PRIMARY KEY (id), 
        FOREIGN KEY(template_id) REFERENCES templates (id), 
        FOREIGN KEY(flavor_id) REFERENCES flavors (id)
    )
{% endquery %}
```
{% endraw %}

{% raw %}
```
{% query 'create_templates' %}
    CREATE TABLE templates (
        id VARCHAR(36) NOT NULL, 
        type VARCHAR(20), 
        name VARCHAR(50), 
        properties VARCHAR(1024), 
        PRIMARY KEY (id)
    )
{% endquery %}
```
{% endraw %}

{% raw %}
```
{% query 'create_clusters', depends_on=['create_templates', 'create_nodes'] %}
    CREATE TABLE clusters (
        id VARCHAR(50) NOT NULL, 
        name VARCHAR(50), 
        template_id VARCHAR(36), 
        FOREIGN KEY(template_id) REFERENCES templates (id)
    )
{% endquery %}
```
{% endraw %}

{% raw %}
```
{% query 'create_flavors' %}
    CREATE TABLE flavors (
        id VARCHAR(36) NOT NULL, 
        properties VARCHAR(1024), 
        PRIMARY KEY (id)
    )
{% endquery %}
```
{% endraw %}

Correct execution order can be fetched with special ```ordered_blocks``` attribute.

```python
migrate_queries = snaql_factory.load_queries('migrations.sql')
solution = migrate_queries.ordered_blocks

# It is a list of ordered functions like
solution = [
    create_flavors_fn
    create_templates_fn,
    create_nodes_fn,
    create_clusters_fn,
]
```
