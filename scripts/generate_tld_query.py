import requests
import json
import sys
from datetime import datetime

def generate_tld_query(tld_count=50):
    try:
        response = requests.get(f"https://isc.sans.edu/api/domaintop/{tld_count}?json")
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Check if response is empty or not valid JSON
        if not response.text.strip():
            print("Error: Empty response from API")
            return
            
        try:
            data = response.json()
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON response. Response text: {response.text[:200]}...")
            return
            
        if not data:
            print("Error: No data returned from API")
            return
            
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
            
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    tld_count = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    generate_tld_query(tld_count) 