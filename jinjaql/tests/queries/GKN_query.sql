{% sql 'top_ten', connection_string='DRIVER=SQL Server;SERVER=DLNWTSR170;Trusted_Connection=Yes' %}
    SELECT TOP 100*
    FROM [{{database}}].dbo.[{{station}}]
    {% if start_date %}
        WHERE [TimeStamp] between '{{start_date}}' and '{{end_date}}'
    {% endif %}
    ORDER BY [TimeStamp] DESC
{% endsql %}