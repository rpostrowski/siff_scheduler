import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

def extract_screenings(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title_tag = soup.find('h1')
    title = title_tag.text.strip() if title_tag else "Unknown Title"

    screenings = []
    
    # Find the section with "Friday, May 16, 2025"
    for day_div in soup.select('.screenings .day'):
        date_text = day_div.find('p', class_='h3')
        if not date_text:
            continue
        if "May 16" not in date_text.get_text():
            continue

        # For each showtime block under this day
        for showtime_div in day_div.select('.listing .item'):
            time_tag = showtime_div.select_one('.button-group a')
            venue_tag = showtime_div.select_one('h4 span.dark-gray-text')
            if not time_tag or not venue_tag:
                continue
            try:
                time_str = time_tag.get_text(strip=True)
                start_time = datetime.strptime("2025 May 16 " + time_str, "%Y %b %d %I:%M %p")
                venue = venue_tag.get_text(strip=True)

                # Extract Running Time (duration in minutes) from the film-detail section
                duration_minutes = None
                film_detail_section = soup.select_one('.details.film-detail')
                if film_detail_section:
                    for li in film_detail_section.find_all('li'):
                        label = li.find('span', class_='label')
                        if label and 'Running Time' in label.get_text():
                            duration_text = li.find('span', class_='detail').get_text(strip=True)
                            # Extract number of minutes
                            duration_minutes = int(duration_text.split()[0])

                if duration_minutes is None:
                    print(f"Running Time not found for {title} at {url}")
                    continue

                screenings.append({
                    "title": title,
                    "start_time": start_time.isoformat(),
                    "location": venue,
                    "url": url,
                    "duration_minutes": duration_minutes
                })
            except Exception as e:
                print(f"Failed to parse time at {url}: {e}")
                continue

    return screenings

def scrape_all():
    FILM_LINKS = [
        "https://www.siff.net/festival/april",
        "https://www.siff.net/festival/bitter-gold",
        "https://www.siff.net/festival/beef",
        "https://www.siff.net/festival/how-to-build-a-library",
        "https://www.siff.net/festival/auction",
        "https://www.siff.net/festival/manas",
        "https://www.siff.net/festival/monk-in-pieces",
        "https://www.siff.net/festival/under-the-volcano",
        "https://www.siff.net/festival/hanami",
        "https://www.siff.net/festival/blue-road-the-edna-obrien-story",
        "https://www.siff.net/festival/drowned-land",
        "https://www.siff.net/festival/billy",
        "https://www.siff.net/festival/ka-whawhai-tonu-struggle-without-end",
        "https://www.siff.net/festival/starman",
        "https://www.siff.net/festival/the-librarians",
        "https://www.siff.net/festival/invention",
        "https://www.siff.net/festival/dancing-queen-in-hollywood",
        "https://www.siff.net/festival/shortsfest-opening-night-x39745",
        "https://www.siff.net/festival/mongrels",
        "https://www.siff.net/festival/alt-shorts-dead-reckoning",
        "https://www.siff.net/festival/the-nature-of-invisible-things",
        "https://www.siff.net/festival/chain-reactions",
        "https://www.siff.net/festival/40-acres",
        "https://www.siff.net/festival/fucktoys"
    ]

    all_screenings = []
    for link in FILM_LINKS:
        try:
            all_screenings.extend(extract_screenings(link))
        except Exception as e:
            print(f"Error scraping {link}: {e}")
    
    with open("may16_screenings.json", "w") as f:
        json.dump(all_screenings, f, indent=2)
    print("Saved to may16_screenings.json")

if __name__ == '__main__':
    scrape_all()