# 🇵🇰 Smart Pakistan Lead Generation Chatbot

An automated Python chatbot designed to generate B2B and B2C business leads specifically targeted in Pakistan. It uses the SerpApi to search Google Maps and Facebook, and features a built-in web scraper to automatically extract contact information (Emails and Pakistani Phone Numbers) from business websites.

##  Features
- **Dual Search Modes:** 
  - **Mode 1 (Google Maps):** Finds local businesses, addresses, and websites.
  - **Mode 2 (Facebook Finder):** Uses Google to locate specific Facebook business pages in Pakistan.
- **Smart Web Scraping:** Automatically visits extracted websites to hunt for `@` emails and `+92` / `03xx` phone numbers using Regex.
- **Pakistan-Optimized:** Hardcoded regional parameters (`gl: pk`) to ensure zero cross-border data leakage.
- **Clean CSV Export:** Automatically formats and saves all leads into a clean, readable Excel/CSV file.
- **Anti-Ban Protection:** Includes polite delays and browser-mimicking headers to prevent IP blocking during web scraping.

##  Prerequisites
- Python 3.x installed
- A free SerpApi Key (Get 100 free searches/month at [serpapi.com](https://serpapi.com/))

##  Installation & Usage

1. Clone this repository:
   ```bash
   git clone <your-repo-url>
   cd <repo-folder>