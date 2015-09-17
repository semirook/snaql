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

{% query 'create_templates' %}
    CREATE TABLE templates (
        id VARCHAR(36) NOT NULL, 
        type VARCHAR(20), 
        name VARCHAR(50), 
        properties VARCHAR(1024), 
        PRIMARY KEY (id)
    )
{% endquery %}

{% query 'create_clusters', depends_on=['create_templates', 'create_nodes'] %}
    CREATE TABLE clusters (
        id VARCHAR(50) NOT NULL, 
        name VARCHAR(50), 
        template_id VARCHAR(36), 
        FOREIGN KEY(template_id) REFERENCES templates (id)
    )
{% endquery %}

{% query 'create_flavors' %}
    CREATE TABLE flavors (
        id VARCHAR(36) NOT NULL, 
        properties VARCHAR(1024), 
        PRIMARY KEY (id)
    )
{% endquery %}
