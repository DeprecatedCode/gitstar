# Request JSON
j: @request.json

# Settings
per_page: {? j ?? per_page: j.per_page, *: 50}$
page:     {? j ?? page:     j.page,     *:  0}$

# Query
query: {}
{? j.query ?? location: query::location ~(j.query.location) }$
{? j.query ?? username: query::username ~(j.query.username) }$
{? j.query ?? name:     query::name     ~(j.query.name)     }$
{? j.query ?? county:   query::county   ~(j.query.county)   }$
{? j.query ?? state:    query::state    ~(j.query.state)    }$
{? j.query ?? language: query::language ~(j.query.language) }$

# Followers and repos >= value
{? j.query ?? followers:  query::followers  {$gte: j.query.followers}$  }$
{? j.query ?? repos:      query::repos      {$gte: j.query.repos}$      }$

# Load Users from Mongo
users: @plugin.mongo {} "github" "user"
objects: users.find(query) \
  .skip (page * per_page) \
  .limit per_page

# Assemble Result JSON
result: {
  count: users.length(query)
  &page, &per_page, pages: count/per_page.ceil
  &objects
}

# Show results
result.to_json.print