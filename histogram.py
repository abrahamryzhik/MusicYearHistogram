# This file is not used by the website, but you can use this to generate the data from your own machine by running this script


import spotipy
from spotipy.oauth2 import SpotifyOAuth

import matplotlib.pyplot as plt

scope = "user-library-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

years = {}

offset = 0

results = sp.current_user_saved_tracks(limit=50)

while len(results['items']) > 0:

    if offset % 1000 == 0:
        print("Analyzing tracks through " + str(offset + 1000))

    for item in results['items']:
        date = item['track']['album']['release_date']
        year = int(date[:date.find('-')])

        if year in years:
            years[year] += 1
        else:
            years[year] = 1

    offset += 50

    results = sp.current_user_saved_tracks(limit=50, offset=offset)

print(years)


# names = list(years.keys())
# values = list(years.values())

min_year = min(years.keys())
max_year = max(years.keys())

print(min_year)
print(max_year)
print(sorted(years.keys()))

sorted_years = sorted(years.keys())

min_year_index = 0

while min_year < 1000 and min_year < sorted_years[-1]:
    min_year_index += 1
    min_year = sorted_years[min_year_index]

print(min_year)
print(max_year)


names = [i for i in range(min_year, max_year+1)]

values = []

for year in names:
    if year in years:
        values.append(years[year])
    else:
        values.append(0)


#plt.bar(range(len(names)), values, tick_label=names)
plt.bar(range(len(names)), values)
plt.xticks(range(len(names)), names, rotation='vertical')
plt.title("My Spotify Saved Tracks")
plt.show()
