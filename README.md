# Snaql. Raw \*QL queries in Python without pain [![Build Status](https://travis-ci.org/semirook/snaql.png)](https://travis-ci.org/semirook/snaql)

Totally inspired by [Yesql](https://github.com/krisajenkins/yesql) from Clojure world. 
But implemented in another way.

## What?

I totally agree with Yesql's author that SQL is already a mature DSL and great abstaction layer 
for DB queries building. And we don't need another layer above SQL to work with RDBMS like ORMs 
or complicated DSLs. Feel free to use all of the SQL's power in your projects without mixing Python 
code and SQL strings. Solution is very simple and flexible enough to try it in your next project. 
Also, Snaql doesn't depend on DB clients, can be used in asynchronous handlers (Tornado, for example). 
It's just a way to organize your queries and a bit of logic to change them by context. Look at examples.

Actually, Snaql doesn't care about stuff you want to build. SQL, SPARQL, SphinxQL, CQL etc., 
you can build any query for any DB or search engine. Freedom.

## Installation

As usual, with pip:

```bash
$ pip install snaql
```

## Documentation

You always can find the most recent docs with examples on [Snaql GitBook](https://semirook.gitbooks.io/snaql/content/)


Simple, without DB clients dependencies (use what you need). Try!

Tested in Python 2.7, 3.3, 3.4, 3.5
