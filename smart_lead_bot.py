import csv
import os
import time
import re
import requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch

# Use absolute path to ensure the CSV saves exactly where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FILENAME = os.path.join(SCRIPT_DIR, "pakistan_smart_leads.csv")
HEADERS = ["Business Name", "Website", "Extracted Email", "Extracted Phone", "Location", "Source", "Notes"]

def setup_file():
    if not os.path.exists(FILENAME):
        with open(FILENAME, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(HEADERS)

def type_effect(text):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(0.015)
    print()

def sanitize_text(text):
    """Removes newlines, carriage returns, and cleans text to prevent CSV breakage."""
    if not text:
        return ""
    # Replace newlines and carriage returns with spaces, replace commas with hyphens
    text = str(text).replace('\n', ' ').replace('\r', ' ').replace(',', ' -')
    # Collapse multiple spaces into a single space
    return ' '.join(text.split()).strip()

def extract_contact_info(url):
    """Visits a website and extracts emails and Pakistani phone numbers."""
    if "facebook.com" in url.lower() or "fb.com" in url.lower():
        return {"email": "Check FB About Page", "phone": "Check FB About Page"}
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text(separator=' ', strip=True)
        
        # Regex for Emails
        emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text_content)))
        emails = [e for e in emails if not e.endswith(('.png', '.jpg', '.css', '.js'))]
        
        # Regex for Pakistani Phone Numbers
        phones = list(set(re.findall(r'(?:\+92|0092|0)[\s\-]?\d{2,4}[\s\-]?\d{6,8}', text_content)))
        
        return {
            "email": ", ".join(emails[:3]) if emails else "Not Found on Website",
            "phone": ", ".join(phones[:3]) if phones else "Not Found on Website"
        }
    except Exception:
        return {"email": "Website Unreachable", "phone": "Website Unreachable"}

def search_google_maps(niche, city, api_key, max_results=15):
    query = f"{niche} in {city}, Pakistan"
    params = {"engine": "google_maps", "q": query, "type": "search", "api_key": api_key, "gl": "pk", "hl": "en"}
    try:
        results = GoogleSearch(params).get_dict()
        places = results.get("local_results", [])
        
        unique_leads = []
        seen_identifiers = set()
        city_lower = city.lower().strip()
        
        for place in places:
            address = place.get("address", "").lower()
            if city_lower not in address:
                continue 
            
            lead = {
                "Business Name": place.get("title", "N/A"),
                "Website": place.get("website", "N/A"),
                "Location": place.get("address", f"{city}, Pakistan"),
                "Source": "Google Maps (PK)",
                "Notes": f"Rating: {place.get('rating', 'N/A')} | {place.get('type', '')}"
            }
            
            # DEDUPLICATION LOGIC
            website = str(lead["Website"]).lower().strip()
            name = lead["Business Name"].lower().strip()
            normalized_url = website.replace("http://", "").replace("https://", "").replace("www.", "").rstrip("/")
            identifier = normalized_url if normalized_url not in ["n/a", ""] else name
            
            if identifier not in seen_identifiers:
                seen_identifiers.add(identifier)
                unique_leads.append(lead)
                
            if len(unique_leads) >= max_results:
                break
                
        return unique_leads

    except Exception as e:
        print(f"[Error]: {e}")
        return []

def search_facebook_pages(niche, city, api_key, max_results=15):
    query = f'site:facebook.com "{niche}" "{city}" "Pakistan"'
    params = {"engine": "google", "q": query, "api_key": api_key, "gl": "pk", "hl": "en"}
    try:
        results = GoogleSearch(params).get_dict()
        organic_results = results.get("organic_results", [])
        leads = []
        for result in organic_results[:max_results]:
            clean_title = result.get("title", "N/A").replace(" - Home | Facebook", "").replace(" | Facebook", "")
            leads.append({
                "Business Name": clean_title,
                "Website": result.get("link", "N/A"),
                "Location": f"{city}, Pakistan",
                "Source": "Facebook (via Google)",
                "Notes": result.get("snippet", "No description")[:80] + "..."
            })
        return leads
    except Exception as e:
        print(f"[Error]: {e}")
        return []

def save_to_csv(leads):
    """Saves leads to CSV with robust sanitization to prevent 'inconsistent fields' errors."""
    sanitized_leads = []
    for lead in leads:
        sanitized_lead = {
            "Business Name": sanitize_text(lead.get("Business Name", "")),
            "Website": sanitize_text(lead.get("Website", "")),
            "Extracted Email": sanitize_text(lead.get("Extracted Email", "")),
            "Extracted Phone": sanitize_text(lead.get("Extracted Phone", "")),
            "Location": sanitize_text(lead.get("Location", "")),
            "Source": sanitize_text(lead.get("Source", "")),
            "Notes": sanitize_text(lead.get("Notes", ""))
        }
        sanitized_leads.append(sanitized_lead)
    
    # QUOTE_ALL ensures that even if a weird character slips through, Excel reads it as one column
    with open(FILENAME, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=HEADERS, quoting=csv.QUOTE_ALL)
        writer.writerows(sanitized_leads)

def main():
    setup_file()
    print("="*60)
    type_effect("[Bot]: 🇵🇰 Welcome to the SMART Pakistan Lead Generator!")
    type_effect("[Bot]: I will find businesses AND automatically extract their Emails & Phones.")
    print("="*60)

    api_key = input("\n[Bot]  Please enter your SerpApi Key: ").strip()
    if not api_key:
        type_effect("[Bot]:  API key is required. Exiting.")
        return

    while True:
        print("\n" + "-"*60)
        type_effect("[Bot]: Choose your search mode:")
        type_effect("  1. Google Maps (Best for finding actual Websites to scrape)")
        type_effect("  2. Facebook Pages (Best for social media, but scraping is limited)")
        
        mode = input("[Bot] ➔ Enter 1 or 2 (or 'exit' to quit): ").strip()
        if mode.lower() == 'exit':
            break
            
        niche = input("[Bot] ➔ Business niche? (e.g., Software House, Salon, Real Estate): ").strip()
        city = input("[Bot] ➔ Which city? (e.g., Karachi, Lahore, Islamabad): ").strip()
        
        try:
            num_results = int(input("[Bot] ➔ How many leads to fetch & scrape? (Max 15 recommended): ").strip())
            num_results = min(num_results, 15)
        except ValueError:
            num_results = 10

        type_effect(f"\n[Bot]:  Step 1: Searching for '{niche}' in {city}, Pakistan...")
        
        if mode == '1':
            raw_leads = search_google_maps(niche, city, api_key, num_results)
        elif mode == '2':
            raw_leads = search_facebook_pages(niche, city, api_key, num_results)
        else:
            type_effect("[Bot]:  Invalid choice. Please enter 1 or 2.")
            continue

        if not raw_leads:
            type_effect("[Bot]:  No results found. Try a different niche.")
            continue

        type_effect(f"\n[Bot]:  Step 2: Automatically visiting {len(raw_leads)} websites to extract Emails & Phones...")
        final_leads = []
        
        for i, lead in enumerate(raw_leads, 1):
            print(f"  [{i}/{len(raw_leads)}] Scraping: {lead['Business Name'][:50]}...", end='\r')
            
            website = lead.get("Website", "N/A")
            if website != "N/A" and str(website).startswith("http"):
                contact_info = extract_contact_info(website)
                lead["Extracted Email"] = contact_info["email"]
                lead["Extracted Phone"] = contact_info["phone"]
            else:
                lead["Extracted Email"] = "No Website Provided"
                lead["Extracted Phone"] = "No Website Provided"
                
            final_leads.append(lead)
            time.sleep(1)

        print(" " * 80, end='\r')
        
        # Save the sanitized data
        save_to_csv(final_leads)
        
        type_effect(f"\n[Bot]:  Success! Processed {len(final_leads)} unique businesses in {city}.")
        type_effect(f"[Bot]:  Clean list saved to: {FILENAME}")
        
        type_effect("\n[Bot]:  Clean Preview of Extracted Data:")
        for i, lead in enumerate(final_leads[:3], 1):
            print(f"  {i}.  {lead['Business Name']}")
            print(f"      {lead['Extracted Email']}")
            print(f"      {lead['Extracted Phone']}")
            print(f"      {lead['Website']}")
            print("-" * 40)
            
        if len(final_leads) > 3:
            type_effect(f"     ... and {len(final_leads) - 3} more in the CSV file!")

        cont = input("\n[Bot]: Search another niche? (yes/no): ").strip().lower()
        if cont not in ['yes', 'y']:
            break

    type_effect("\n[Bot]:  All done! Open the CSV file in Excel. Khuda Hafiz!")

if __name__ == "__main__":
    main()
