#!/usr/bin/env python3
&quot;&quot;&quot;
Fetch Census data for Indiana ZIP codes and geocode.
&quot;&quot;&quot;

import requests
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time
import json
import sys

def fetch_census_zips():
    &quot;&quot;&quot;Fetch ACS5 data for IN ZCTAs.&quot;&quot;&quot;
    url = &quot;https://api.census.gov/data/2022/acs/acs5?get=NAME,B01003_001E,B19013_001E,B25064_001E&amp;for=zip%20code%20tabulation%20area:*&amp;in=state:18&quot;
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    df = pd.DataFrame(data[1:], columns=data[0])
    df[&quot;population&quot;] = pd.to_numeric(df[&quot;B01003_001E&quot;], errors=&quot;coerce&quot;)
    df[&quot;median_income&quot;] = pd.to_numeric(df[&quot;B19013_001E&quot;], errors=&quot;coerce&quot;)
    df[&quot;median_rent&quot;] = pd.to_numeric(df[&quot;B25064_001E&quot;], errors=&quot;coerce&quot;)
    df[&quot;zip&quot;] = df[&quot;zip code tabulation area&quot;]
    # Filter viable zips
    df = df[(df[&quot;population&quot;] &gt; 500) &amp; (df[&quot;population&quot;] &lt; 100000)].copy()
    return df[[&quot;zip&quot;, &quot;population&quot;, &quot;median_income&quot;, &quot;median_rent&quot;]]

def geocode_zip(zip_code):
    geolocator = Nominatim(user_agent=&quot;zipforge_app&quot;)
    try:
        location = geolocator.geocode(f&quot;{zip_code}, Indiana&quot;, timeout=10)
        if location:
            return location.latitude, location.longitude
    except:
        pass
    return None, None

def add_coords(df):
    coords = []
    for zip_code in df[&quot;zip&quot;]:
        lat, lon = geocode_zip(zip_code)
        coords.append((lat, lon))
        print(f&quot;Geocoded {zip_code}: ({lat}, {lon})&quot;)
        time.sleep(1.1)  # Nominatim rate limit
    df[&quot;lat&quot;] = [c[0] for c in coords]
    df[&quot;lon&quot;] = [c[1] for c in coords]
    return df.dropna(subset=[&quot;lat&quot;])

if __name__ == &#x27;__main__&#x27;:
    print(&quot;Fetching Census data for IN ZIPs...&quot;)
    df = fetch_census_zips()
    print(f&quot;Fetched {len(df)} candidate ZIPs&quot;)
    print(&quot;Geocoding (this takes ~1min per 10 ZIPs)...&quot;)
    df = add_coords(df)
    print(f&quot;Successfully geocoded {len(df)} ZIPs&quot;)
    df.to_json(&#x27;zips_census.json&#x27;, orient=&#x27;records&#x27;, indent=2)
    with open(&#x27;zips.txt&#x27;, &#x27;w&#x27;) as f:
        f.write(&#x27;\n&#x27;.join(df[&#x27;zip&#x27;].astype(str)))
    print(&quot;✅ Saved zips_census.json and updated zips.txt&quot;)
