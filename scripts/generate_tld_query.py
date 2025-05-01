import requests
import json
import sys
import time
from datetime import datetime

def generate_tld_query(tld_count=50):
    try:
        url = f"https://isc.sans.edu/api/domaintop/{tld_count}?json"
        print(f"Making request to: {url}")
        
        # Add a delay before the first request
        print("Waiting 5 seconds before making request...")
        time.sleep(5)
        
        response = requests.get(url)
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        
        # If we get HTML, wait and retry
        if 'text/html' in response.headers.get('content-type', ''):
            print("Received HTML response, waiting 10 seconds and retrying...")
            time.sleep(10)
            response = requests.get(url)
            print(f"Retry response status code: {response.status_code}")
            print(f"Retry response headers: {response.headers}")
        
        response.raise_for_status()
        
        # Check if response is empty or not valid JSON
        if not response.text.strip():
            print("Error: Empty response from API")
            return
            
        print(f"Response text preview: {response.text[:200]}...")
            
        try:
            data = response.json()
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON response. Response text: {response.text[:200]}...")
            return
            
        if not data:
            print("Error: No data returned from API")
            return
            
        print(f"Parsed JSON data: {json.dumps(data, indent=2)[:200]}...")
            
        tlds = [item["domain"].split(".")[-1] for item in data]
        
        query = f"""EmailEvents
| where RecipientEmailAddress endswith ({' or '.join(f'"{tld}"' for tld in tlds)})
| summarize count() by RecipientEmailAddress, SenderFromAddress, Subject
| order by count_ desc"""

        # Save the query to a .txt file
        with open("tld_query.txt", "w") as f:
            f.write(query)
            
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    tld_count = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    generate_tld_query(tld_count) 