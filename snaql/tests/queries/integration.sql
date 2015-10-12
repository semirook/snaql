{% query 'create_artists' %}
    CREATE TABLE artists (
        id INTEGER NOT NULL, 
        name VARCHAR(50), 
        age INTEGER,
        instrument VARCHAR(50), 
        PRIMARY KEY (id)
    );
{% endquery %}

{% query 'drop_artists' %}
    DROP TABLE artists;
{% endquery %}

{% query 'insert_artist' %}
    INSERT INTO artists
    VALUES ({{ id|guards.integer }}, {{ name|guards.string }}, {{ age|guards.integer }}, {{ instrument|guards.string }});
{% endquery %}


{% sql 'get_artists', note='get artists' %}
    SELECT name, age, instrument
    FROM artists
    WHERE id = {{ id }};
{% endsql %}
