import requests
import json
import sys
import time
from datetime import datetime
from collections import Counter

def generate_tld_query(tld_count=50):
    try:
        url = "https://isc.sans.edu/api/recentdomains?json"
        print(f"Making request to: {url}")
        
        # Add a longer initial delay
        print("Waiting 15 seconds before making request...")
        time.sleep(15)
        
        max_retries = 3
        retry_count = 0
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
        while retry_count < max_retries:
            response = requests.get(url, headers=headers)
            print(f"Response status code: {response.status_code}")
            print(f"Response headers: {response.headers}")
            
            # Check if we got JSON
            if 'application/json' in response.headers.get('content-type', ''):
                break
                
            # If we got HTML, wait longer and retry
            print(f"Received non-JSON response (attempt {retry_count + 1}/{max_retries})")
            print("Waiting 20 seconds before retrying...")
            time.sleep(20)
            retry_count += 1
        
        if retry_count == max_retries:
            print("Max retries reached. Could not get JSON response.")
            return
            
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
            
        # Extract TLDs and count their occurrences
        tlds = [domain["domainname"].split(".")[-1] for domain in data if domain["domainname"]]
        tld_counts = Counter(tlds)
        
        # Get top N TLDs
        top_tlds = [tld for tld, _ in tld_counts.most_common(tld_count)]
        
        query = f"""EmailEvents
| where RecipientEmailAddress endswith ({' or '.join(f'"{tld}"' for tld in top_tlds)})
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