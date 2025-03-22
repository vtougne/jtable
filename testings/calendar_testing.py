#!/usr/bin/env python3

import json
from datetime import datetime, timedelta

# Nombre de jours à générer (1 an)
DAYS = 365

# Date de départ : aujourd'hui
today = datetime.today()

# Génération du calendrier
calendar = []
for i in range(DAYS):
    date = today + timedelta(days=i)
    calendar.append({
        "date": date.strftime("%Y-%m-%d %H:%M:%S"),
        "day_of_week": date.strftime("%A")
    })

# Export en JSON
# calendar_json = json.dumps(calendar, indent=4, ensure_ascii=False)
calendar_json = json.dumps(calendar)
print(calendar_json)
