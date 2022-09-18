<div align="center">
<!-- Title: -->
<h1>URL Shortener</h1>
<!-- Description: -->
<p>URL Shortener is a simple web application that allows you to shorten URLs.</p>
</div>

<!-- Table of Contents: -->
<div align="left">
<h2>Table of Contents</h2>
<ol>
<li><a href="#about">About</a></li>
<li><a href="#getting-started">Getting Started</a></li>
<li><a href="#usage">Usage</a></li>
</ol>

</div>
 
<!-- About: -->
<div align="left">
<h2 id="about">About</h2>
<p>URL Shortener is a simple web application that allows you to shorten URLs.</p>
</div>
 
<!-- Getting Started: -->
<div align="left">
<h2 id="getting-started">Getting Started</h2>
<p>
<h3>Setup</h3>
<!-- Docker -->
<p>
<h4>Docker</h4>
<ol>
<li>Install Docker</li>
<li>Clone the repository</li>
<li>Run the following command in the root directory of the project: <code>docker-compose up --build</code></li>
</ol>

</p>
<!-- Usage: -->
<div align="left">
<h2 id="usage">Usage</h2>
<p>
<h3>API</h3>
Note: The documentation is available at <a href="http://localhost:8000/redoc">http://localhost:8000/redoc</a> after running the application.
<p>
<h3>Sample Requests</h3>
<p>
<h4>Shorten URL</h4>

```bash
curl -X POST "http://localhost:8000/url_shortener/" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"url\": \"https://www.google.com/\"}"
```
<!-- Response -->

```json
{
  "url": "https://www.google.com/",
  "short_url": "abc123",
  "on_clicks": 0,
  "created": "2021-09-12T20:00:00.000000Z"
}
```

</p>
<p>
<h4>Get List of URLs</h4>

```bash
curl -X GET "http://localhost:8000/urls/" -H "accept: application/json"
```

<!-- Response -->

```json
[
  {
    "url": "https://www.google.com/",
    "short_url": "abc123",
    "created": "2021-09-12T20:00:00.000000Z"
  }
]
```

</p>
<p>
<h4>Reroute to URL</h4>

```bash
curl -X GET "http://localhost:8000/url/abc123/" -I -o /dev/null -w '%{http_code}\n' -s
```

<!-- Response -->

```bash
302
```

Note: This will redirect you to the URL.

</p>

<h4>Get URL Details</h4>

```bash
curl -X GET "http://localhost:8000/info/abc123/" -H "accept: application/json"
```

<!-- Response -->

```json
{
  "url": "https://www.google.com/",
  "on_clicks": 1,
  "created": "2021-09-12T20:00:00.000000Z"
}
```

</p>

<h4>Delete URL</h4>

```bash
curl -X DELETE 'http://localhost:8000/info/abc123/' -LI -o /dev/null -w '%{http_code}\n' -s
```

<!-- Response -->

<!-- Return 204 -->
```
204
```


</p>

</p>
</div>
 
<!-- Notes: -->
<div align="left">
<h2>Notes</h2>
<p>
<h3>Database</h3>
<p>
The database is a PostgreSQL database.
</p>
</p>
<h3>API</h3>
<p>
The API is built using Django REST Framework.
</p>
<h3>Algorithm for Shortening URLs</h3>
<p>
    The algorithm used to generate the shortened URL is seeded with the last URL's ID. This means that if the last URL's ID is 0, the algorithm will start from 0. If the last URL's ID is 1, the algorithm will start from 1. This is to ensure that the shortened URLs are unique.(The output of the algorithm is a string of characters chosen randomly from the set of characters in `ascii_letters + digits` and the length of the string is equal to the `max_length` of the `short_url` field in the `Url` model.)<br>
    The use of seed was to prevent the replication of random generator loop. For example, if the loop method was used, it would be necessary to check our database for the existence of the generated string. This would be a costly operation. The use of seed ensures that the algorithm will not repeat itself.<br>
    All the steps above are done in the database(you can see the SQL query in the `url_shortener/migrations/queries/sql_generator.text` file).<br>This is to ensure that the database is not locked for a long time.
</p>

<h3>Caching</h3>
<p>
    The caching is done using Redis.
</p>

</div>
