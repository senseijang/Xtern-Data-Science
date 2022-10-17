#!/usr/bin/env python
# coding: utf-8

# In[104]:


import requests
from urllib.parse import urlencode, urlparse, parse_qsl
import csv
import pandas as pd


# In[105]:


GOOGLE_API_KEY = "AIzaSyCQLnUynI4y2NUzr1behot71QopvpZy3QU"


# ### Google Maps Client API

# In[106]:


class GoogleMapsClient(object):
    lat = None
    lng = None
    data_type = 'json'
    location_query = None
    api_key = None

    def __init__(self, api_key=None, address=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if api_key == None:
            raise Exception("API key is required")
        self.api_key = api_key
        self.location_query = address
        if self.location_query != None:
            self.extract_lat_lng()

    def extract_lat_lng(self, location=None):
        loc_query = self.location_query
        if location != None:
            loc_query = location
        data_type = "json"
        endpoint = f"https://maps.googleapis.com/maps/api/geocode/{self.data_type}"
        params = {"address": loc_query, "key": self.api_key}
        url_params = urlencode(params)
        url = f"{endpoint}?{url_params}"
        r = requests.get(url)
        if r.status_code not in range(200, 299):
            return {}
        lat_lng = {}
        try:
            lat_lng = r.json()["results"][0]["geometry"]["location"]
        except:
            pass
        lat, lng = lat_lng.get("lat"), lat_lng.get("lng")
        self.lat = lat
        self.lng = lng
        return lat, lng

    def search(self, keyword="Attractions", radius=1000, location=None):
        lat, lng = self.lat, self.lng
        if location != None:
            lat, lng = self.extract_lat_lng(location)
        places_endpoint = f"https://maps.googleapis.com/maps/api/place/nearbysearch/{self.data_type}"
        params = {
            "key": self.api_key,
            "location": f"{lat},{lng}",
            "radius": radius,
            "keyword": keyword
        }
        params_encoded = urlencode(params)
        places_url = f"{places_endpoint}?{params_encoded}"

        r = requests.get(places_url)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()

    def detail(self, place_id="ChIJK1-_KkxXa4gRazRkyTLNKBw"):
        detail_base_endpoint = "https://maps.googleapis.com/maps/api/place/details/json"
        detail_params = {
            "place_id": f"{place_id}",
            "fields": "name,rating,formatted_phone_number,formatted_address,website,url,types",
            "key": self.api_key
        }

        detail_params_encoded = urlencode(detail_params)
        detail_url = f"{detail_base_endpoint}?{detail_params_encoded}"

        r = requests.get(detail_url)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()


# In[121]:


client = GoogleMapsClient(api_key=GOOGLE_API_KEY, address="Indianapolis, IN")

# print(client.search("Food", radius=2000, location="Fishers, IN")["results"][0].keys())
# print(client.search("Food", radius=2000, location="Indianapolis, IN")["results"][0]['price_level'])


# In[142]:


# In a 3 mile radius of the lat, lng of Indianapolis
results = client.search("Attractions", radius=5000,
                        location="Indianapolis, IN")["results"]
results += client.search("Gift Shops", radius=5000,
                         location="Indianapolis, IN")["results"]
results += client.search("Restaurants", radius=5000,
                         location="Indianapolis, IN")["results"]
"""
print(f"#,Name,Address,Rating,Website,Type")
for i in range(len(results)):
    curr = results[i]
    try:
        website = client.detail(place_id=curr['place_id'])['result']['website']
        print(f"{i+1},{curr['name']},{curr['vicinity']},{curr['rating']},{website},{curr['types'][0]}\n")
    except:
        print(f"{i+1},{curr['name']},{curr['vicinity']},{curr['rating']},NULL,{curr['types'][0]}\n")
"""
with open('mapData.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Name', 'Address', 'Rating', 'Website', 'Type'])
    for i in range(len(results)):
        curr = results[i]
        # omit if rating is less than 4 stars
        if curr['rating'] < 4:
            continue
        try:
            website = client.detail(place_id=curr['place_id'])[
                'result']['website']
        except:
            website = "NULL"
        writer.writerow([curr['name'], curr['vicinity'],
                        curr['rating'], website, curr['types'][0]])


# In[143]:


dataset = pd.read_csv("mapData.csv")
dataset.head(9999)


# In[ ]:
