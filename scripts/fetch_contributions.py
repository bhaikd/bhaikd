import os
import sys
import json
import re
from datetime import datetime, date, timezone

def fetch_contributions(username="bhaikd", output_file="data/contributions.json"):
    url = f"https://github.com/users/{username}/contributions"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    print(f"Fetching contribution calendar from '{url}'...")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching data: HTTP {response.status_code}")
        sys.exit(1)

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Tooltips mapping by ID if available
    tooltips = {}
    for tt in soup.find_all(["tool-tip", "div"], id=True):
        tooltips[tt["id"]] = tt.get_text(strip=True)

    day_elements = soup.find_all(attrs={"data-date": True})
    if not day_elements:
        print("Warning: No contribution day elements found in HTML response.")

    days = []
    total_count = 0

    for elem in day_elements:
        day_date = elem.get("data-date")
        level_attr = elem.get("data-level", "0")
        try:
            level = int(level_attr)
        except ValueError:
            level = 0

        # Try getting count directly or from attributes / tooltips
        count = 0
        if elem.has_attr("data-count"):
            try:
                count = int(elem["data-count"])
            except ValueError:
                count = 0
        else:
            # Check id or tooltip
            elem_id = elem.get("id", "")
            tooltip_txt = tooltips.get(elem_id, "")
            if not tooltip_txt:
                tooltip_elem = soup.find(attrs={"for": elem_id})
                if tooltip_elem:
                    tooltip_txt = tooltip_elem.get_text(strip=True)
                else:
                    tooltip_txt = elem.get_text(strip=True)

            # Match numbers in tooltip e.g. "5 contributions on January 1, 2024" or "No contributions..."
            match = re.search(r"(\d+)\s+contribution", tooltip_txt, re.IGNORECASE)
            if match:
                count = int(match.group(1))
            elif "No contribution" in tooltip_txt:
                count = 0
            else:
                # Estimate count from level if parsing count fails
                level_estimates = {0: 0, 1: 1, 2: 3, 3: 6, 4: 10}
                count = level_estimates.get(level, level * 2)

        days.append({
            "date": day_date,
            "level": level,
            "count": count
        })
        total_count += count

    # Sort chronologically by date
    days.sort(key=lambda d: d["date"])

    # Calculate streaks & best day
    current_streak = 0
    longest_streak = 0
    temp_streak = 0
    best_day = {"date": None, "count": 0}

    for d in days:
        cnt = d["count"]
        if cnt > best_day["count"]:
            best_day = {"date": d["date"], "count": cnt}
        
        if cnt > 0:
            temp_streak += 1
            if temp_streak > longest_streak:
                longest_streak = temp_streak
        else:
            temp_streak = 0

    # Calculate current streak backwards from latest day
    today_str = date.today().isoformat()
    idx = len(days) - 1
    # If today has 0 contributions, we allow current streak to include up to yesterday
    if idx >= 0 and days[idx]["count"] == 0 and days[idx]["date"] == today_str:
        idx -= 1

    while idx >= 0 and days[idx]["count"] > 0:
        current_streak += 1
        idx -= 1

    # Monthly totals
    monthly_totals = {}
    for d in days:
        month_key = d["date"][:7] # YYYY-MM
        monthly_totals[month_key] = monthly_totals.get(month_key, 0) + d["count"]

    result_data = {
        "username": username,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total_contributions": total_count,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly_totals": monthly_totals,
        "days": days
    }

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result_data, f, indent=2)

    print(f"Successfully scraped {len(days)} days ({total_count} total contributions). Saved to '{output_file}'.")

if __name__ == "__main__":
    uname = sys.argv[1] if len(sys.argv) > 1 else "bhaikd"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "data/contributions.json"
    fetch_contributions(uname, out_path)
