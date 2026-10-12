# City Beautiful Buzz 🏙️
### A hyper-local Chandigarh news widget for macOS

---

## What is this?
**City Beautiful Buzz** is a native macOS widget (built with SwiftUI + WidgetKit) that surfaces real-time, hyper-local news and events for **Chandigarh (Tricity)**. 

It aggregates news from 10+ sources including The Tribune, Hindustan Times, Indian Express, Dainik Jagran, Punjab Kesari, AllEvents.in and more — deduplicated, categorized, and delivered as a clean widget on your Mac desktop.

---

## Architecture
```
GitHub Actions (every 15 min)
    → Python Scraper (RSS + Web)
        → news.json
            → GitHub Pages (free API)
                → macOS WidgetKit (Swift)
```

## Categories Covered
- ⚠️ Alerts (water cuts, power outages, weather)
- 🏗️ Infrastructure (roads, construction, smart city)
- 🏛️ Governance (MC decisions, court orders)
- 🎭 Events (festivals, concerts, exhibitions)
- 📅 Key Dates (deadlines, registration, exams)
- 📚 Education (PU, schools, admissions)
- 🏥 Health (PGIMER, camps, disease alerts)
- 🏏 Sports (local tournaments, stadium events)
- 🍽️ Lifestyle (restaurants, cafés, launches)
- 🔐 Safety (crime alerts, traffic updates)

## News Sources
| Source | Type | Language |
|---|---|---|
| Hindustan Times Chandigarh | RSS | EN |
| The Tribune | RSS + Web | EN |
| Indian Express Chandigarh | RSS | EN |
| NDTV Chandigarh | RSS | EN |
| Dainik Jagran Chandigarh | RSS | HI |
| Punjab Kesari | RSS | HI |
| Amar Ujala Chandigarh | RSS | HI |
| Chandigarh Media | Web | EN |
| Chandigarh Bytes | Web | EN |
| AllEvents.in Chandigarh | Web | EN |

## Setup

### Backend (this repo)
```bash
# 1. Clone this repo
git clone https://github.com/YOUR_USERNAME/city-beautiful-buzz.git
cd city-beautiful-buzz

# 2. Install dependencies
pip3 install -r Backend/requirements.txt

# 3. Test locally (dry run)
python3 Backend/scraper.py --test

# 4. Run for real
python3 Backend/scraper.py
# Output: Backend/data/news.json
```

### GitHub Pages (free API hosting)
1. Push this repo to GitHub
2. Go to **Settings → Pages → Source**: set to `main` branch, `/ (root)` folder
3. Your JSON API will be live at:
   `https://customonion4321.github.io/city-beautiful-buzz/Backend/data/news.json`

### Update `normalizer.py`
The normalizer is already pre-configured with your URL:
```python
GITHUB_PAGES_BASE = "https://customonion4321.github.io/city-beautiful-buzz"
```

### macOS Widget (Xcode)
See the `CityBeautifulBuzz/` directory for the Swift/SwiftUI code.

---

## License
Personal use only. News content belongs to respective publishers.
