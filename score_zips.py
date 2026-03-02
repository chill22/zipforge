#!/usr/bin/env python3
&quot;&quot;&quot;
Score ZIPs using xAI Grok API based on census data.
Requires .env: GROK_API_KEY from https://console.x.ai
&quot;&quot;&quot;

import os
import json
import pandas as pd
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

if not os.getenv(&quot;GROK_API_KEY&quot;):
    print(&quot;❌ Set GROK_API_KEY in .env&quot;)
    exit(1)

client = OpenAI(
    api_key=os.getenv(&quot;GROK_API_KEY&quot;),
    base_url=&quot;https://api.x.ai/v1&quot;,
)

def score_zip(census_row):
    data_str = f&quot;&quot;&quot;
ZIP: {census_row[&#x27;zip&#x27;]}
Population: {int(census_row[&#x27;population&#x27;]):,}
Median Income: ${int(census_row[&#x27;median_income&#x27;]):,}
Median Rent: ${int(census_row[&#x27;median_rent&#x27;]):,} if &#x27;median_rent&#x27; in census_row else &#x27;N/A&#x27;
    &quot;&quot;&quot;
    prompt = f&quot;&quot;&quot;Score 0-100 how desirable this Indiana ZIP is for families.
High: good balance income/population, affordable rent, vibrant.
Low: low income, high rent/poverty implied.

{census_row}

ONLY respond with number e.g. &#x27;75.3&#x27;&quot;&quot;&quot;
    
    try:
        resp = client.chat.completions.create(
            model=&quot;grok-beta&quot;,
            messages=[{&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: prompt}],
            temperature=0.2,
            max_tokens=5
        )
        score_text = resp.choices[0].message.content.strip()
        score = float(score_text)
        return max(0, min(100, score))
    except Exception as e:
        print(f&quot;⚠️ Error scoring {census_row[&#x27;zip&#x27;]}: {e}&quot;)
        return 50.0

if __name__ == &#x27;__main__&#x27;:
    if not os.path.exists(&#x27;zips_census.json&#x27;):
        print(&quot;❌ Run fetch_data.py first!&quot;)
        sys.exit(1)
    
    df = pd.read_json(&#x27;zips_census.json&#x27;)
    print(f&quot;Scoring {len(df)} ZIPs... (add your GROK_API_KEY)&quot;)
    scores = []
    for idx, row in df.iterrows():
        print(f&quot;Scoring ZIP {row[&#x27;zip&#x27;]} ({idx+1}/{len(df)})...&quot;)
        score = score_zip(row)
        scores.append({
            &quot;zip&quot;: row[&#x27;zip&#x27;],
            &quot;score&quot;: round(score, 1),
            &quot;lat&quot;: row[&#x27;lat&#x27;],
            &quot;lon&quot;: row[&#x27;lon&#x27;],
            &quot;favorite&quot;: False
        })
        time.sleep(3)  # Conservative rate limit
    
    with open(&#x27;scores.json&#x27;, &#x27;w&#x27;) as f:
        json.dump(scores, f, indent=2)
    
    print(&quot;✅ Real scores saved to scores.json&quot;)
