# MusicYearHistogram

MusicYearHistogram is a project to build a web app to allow Spotify users to analyze their music library by year. Users log in with their Spotify account and the app presents them with a bar graph showing how many tracks there are for each year. Currently we only pull from their saved tracks but we may later also include recent tracks, top tracks, and playlists.

## File Organization

The app is created using [Flask](https://flask.palletsprojects.com/en/2.2.x/) so the flaskr folder is where the entire app lies. __init__.py contains all of the main code for the app. The templates folder contains all of the HTML templates and the static folder contains CSS and images. If you want to run the program just as a script, histogram.py runs the same process as the web app with a regular python script and mymusicyearhistogram.py shows an example output.

## Main Packages Used

As mentioned before, the main app is built using Flask. To access the Spotify Web API with Python I use [spotipy](https://spotipy.readthedocs.io/en/2.22.1/). The app is deployed on [PythonAnywhere](https://www.pythonanywhere.com/) at this [link](https://abrahamryzhik.pythonanywhere.com/index) however since the app is still in development mode with Spotify, only users whose email I add directly will have access to the app. Plots are made using [matplotlib](https://matplotlib.org/).
