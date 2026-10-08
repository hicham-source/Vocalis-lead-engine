import os
import requests
from database import get_connection

def fetch_places(niche, district):
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    url = "https://places.googleapis.com/v1/places:searchText"
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.nationalPhoneNumber,places.websiteUri,places.googleMapsUri,nextPageToken"
    }
    
    payload = {
        "textQuery": f"{niche} in {district}, Riyadh"
    }
    
    conn = get_connection()
    c = conn.cursor()
    results_fetched = 0

    while True:
        response = requests.post(url, headers=headers, json=payload).json()
        places = response.get("places", [])
        
        for place in places:
            place_id = place.get("id")
            phone = place.get("nationalPhoneNumber")
            
            # Check Opt-out
            c.execute("SELECT 1 FROM opt_out WHERE identifier = ?", (place_id,))
            if c.fetchone():
                continue
            if phone:
                c.execute("SELECT 1 FROM opt_out WHERE identifier = ?", (phone,))
                if c.fetchone():
                    continue
                    
            # Check already exists
            c.execute("SELECT 1 FROM leads WHERE place_id = ?", (place_id,))
            if c.fetchone():
                continue

            name = place.get("displayName", {}).get("text", "")
            address = place.get("formattedAddress", "")
            rating = place.get("rating")
            review_count = place.get("userRatingCount")
            website = place.get("websiteUri")
            maps_url = place.get("googleMapsUri")

            c.execute('''
                INSERT INTO leads (place_id, name, address, rating, review_count, phone, website, maps_url, niche)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (place_id, name, address, rating, review_count, phone, website, maps_url, niche))
            
            results_fetched += 1

        conn.commit()
        
        next_page_token = response.get("nextPageToken")
        if next_page_token:
            payload["pageToken"] = next_page_token
        else:
            break
            
    conn.close()
    print(f"[Discovery] Added {results_fetched} new leads for {niche} in {district}.")
