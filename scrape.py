from mongoengine import *
import requests
import urllib

# Import Location Data
from california_locations import state, counties, blacklist

# Connect to Mongo
connect('github')

# City Model
class City(Document):
  name = StringField()
  county = StringField()
  state = StringField()
  completed = BooleanField()
  
# User Model
class User(Document):
  username = StringField()
  name = StringField()
  email = StringField()
  city = ReferenceField(City)
  
  county = StringField()
  state = StringField()

  location = StringField()
  language = StringField()
  
  repos = IntField()
  followers = IntField()
  
if True:
  import ipdb
  ipdb.set_trace()
  
# Scrape Github URL
url_for_page = "https://api.github.com/legacy/user/search/{}?sort=followers&order=desc&per_page=100&start_page={}&access_token=%TOKEN%".format

# Query to Format
query = {
  'followers': '>3',
  'repos': '>0'
}

# Format Query
def fmt_query(q):
  s = []
  for key, value in q.items():
    s.append("{}:{}".format(key, value.replace('>', '%3E').replace(' ', '+')))
  return '%20'.join(s)

# Read Access Token
with open('.token') as file:
  token = file.read()
  
for county, cities in counties.iteritems():
  for name in cities:

    # Create city if not exists
    try:
      city = City.objects.get(name=name, county=county, state=state)
    except DoesNotExist:
      print "Creating city..."
      city = City(name=name, county=county, state=state).save()
      
    if city.completed:
      print "\n[x] Already completed: {} in {} County, {}".format(city.name, city.county, city.state)
      continue

    print "\n[ ] Processing: {} in {} County, {}".format(city.name, city.county, city.state)
    
    query['location'] = city.name

    page = 0
    count = 0
    while True:
      page += 1
      
      url = url_for_page(fmt_query(query), page).replace('%TOKEN%', token)
      print " {} {}".format(page, url)
      
      data = requests.get(url).json()
      if not 'users' in data:
        raise Exception("Message: {}".format(data['message']))
      
      if len(data['users']) == 0:
        break

      for udata in data['users']:

        # Skip existing user documents
        try:
          User.objects.get(username=udata['username'])
          continue
        except DoesNotExist:
          pass
        
        # Check user location against the blacklist
        check = udata.get('location', '')
        bad = False
        for word in blacklist:
          if word in check:
            bad = True
        if bad:
          continue

        user = User(
          username=udata['username'],
          name=udata.get('fullname'),
          email=udata.get('email'),
          city=city,
          county=city.county,
          state=city.state,
          location=udata.get('location'),
          language=udata.get('language'),
          repos=udata.get('repos'),
          followers=udata.get('followers')
        )
        user.save()
        count += 1
        
      if len(data['users']) < 100:
        break
      
    print ' = {} users'.format(count)

    city.completed = True
    city.save()