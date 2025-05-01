import requests
import json
import sys
from datetime import datetime

def generate_tld_query(tld_count=50):
    response = requests.get(f"https://isc.sans.edu/api/domaintop/{tld_count}?json")
    data = response.json()
    tlds = [item["domain"].split(".")[-1] for item in data]
    
    query = f"""EmailEvents
| where RecipientEmailAddress endswith ({' or '.join(f'"{tld}"' for tld in tlds)})
| summarize count() by RecipientEmailAddress, SenderFromAddress, Subject
| order by count_ desc"""

    output = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "tlds": tlds,
        "query": query
    }

    with open("tld_query.json", "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    tld_count = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    generate_tld_query(tld_count) 