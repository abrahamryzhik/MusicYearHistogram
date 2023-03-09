import os

from flask import Flask, render_template, redirect, request, session, make_response,session,redirect, Response
import spotipy
import spotipy.util as util
#from credentz import *
import time
import json

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

import io

from spotify_config import REDIRECT_URI, CLI_ID, CLI_SEC

API_BASE = 'https://accounts.spotify.com'

SCOPE = "user-library-read,playlist-modify-private,playlist-modify-public,user-top-read"

#app.secret_key = SSK



SHOW_DIALOG = True

#years = {}

user_to_data = {}

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route("/")
    def verify():
        # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
        sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = CLI_ID, client_secret = CLI_SEC, redirect_uri = REDIRECT_URI, scope = SCOPE)
        auth_url = sp_oauth.get_authorize_url()
        print(auth_url)
        return redirect(auth_url)

    @app.route("/index")
    def index():
        return render_template("home.html")

    # authorization-code-flow Step 2.
    # Have your application request refresh and access tokens;
    # Spotify returns access and refresh tokens
    @app.route("/api_callback")
    def api_callback():
        # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
        sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = CLI_ID, client_secret = CLI_SEC, redirect_uri = REDIRECT_URI, scope = SCOPE)
        session.clear()
        code = request.args.get('code')
        token_info = sp_oauth.get_access_token(code)

        # Saving the access token along with all other token related info
        session["token_info"] = token_info


        return redirect("index")

    # authorization-code-flow Step 3.
    # Use the access token to access the Spotify Web API;
    # Spotify returns requested data
    @app.route("/go", methods=['POST', 'GET'])
    def go():

        #if request.method == 'POST' or request.method == 'GET':
        #print("here0")
        session['token_info'], authorized = get_token(session)
        session.modified = True
        #print("here1")
        if not authorized:
            return redirect('/')
        data = request.form
        sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
        #print("here2")
        #response = sp.current_user_top_tracks(limit=data['num_tracks'], time_range=data['time_range'])

        results = sp.current_user_saved_tracks(limit=1)

        me = sp.current_user()
        print(me['display_name'])
        print(me['id'])


        if request.method == 'GET' and me['id'] in user_to_data:
            years = user_to_data[me['id']]
            biggest_year = max(years, key=years.get)

            return render_template("results.html", data=request.form, biggest_year=biggest_year)

        track = results['items'][0]['track']['name']
        #print(track)


        #print("here3")

        years = {}

        offset = 0

        results = sp.current_user_saved_tracks(limit=50)

        while len(results['items']) > 0:

            if offset % 1000 == 0:
                print("Analyzing tracks through " + str(offset + 1000))
                render_template("loading.html", song_num=offset+1000)

            for item in results['items']:
                date = item['track']['album']['release_date']
                year = int(date[:date.find('-')])

                if year in years:
                    years[year] += 1
                else:
                    years[year] = 1

            offset += 50

            results = sp.current_user_saved_tracks(limit=50, offset=offset)

        #print(data)



        # data = {"dummyv" : "woohoo"}


        #print(years)

        biggest_year = max(years, key=years.get)

        user_to_data[me['id']] = years


        # print(json.dumps(response))

        return render_template("results.html", data=data, biggest_year=biggest_year)
        # else:
        #     print("doing the go")
        #     biggest_year = max(years, key=years.get)

        #     return render_template("results.html", data=request.form, biggest_year=biggest_year)

 
    @app.route('/plot.png')
    def plot_png():
        fig = create_figure()
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')

    def create_figure():

        session['token_info'], authorized = get_token(session)
        session.modified = True
        #print("here1")
        if not authorized:
            return redirect('/')


        
        sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))

        me = sp.current_user()
        print("and now from create figure:")
        print(me['display_name'])
        print(me['id'])

        years = user_to_data[me['id']]




        min_year = min(years.keys())
        max_year = max(years.keys())


        sorted_years = sorted(years.keys())

        min_year_index = 0

        while min_year < 1000 and min_year < sorted_years[-1]:
            min_year_index += 1
            min_year = sorted_years[min_year_index]



        names = [i for i in range(min_year, max_year+1)]

        values = []

        for year in names:
            if year in years:
                values.append(years[year])
            else:
                values.append(0)
        fig = Figure(figsize=[8,3], dpi=200)
        axis = fig.add_subplot(1, 1, 1)
        # xs = range(100)
        # ys = [random.randint(1, 50) for x in xs]
        axis.bar(range(len(names)), values)
        #axis.set_xticks(range(len(names)), labels=names, rotation='vertical')
        axis.set_xticks(range(len(names)))
        axis.set_xticklabels(names, rotation='vertical', fontdict={'fontsize':5})
        # axis.plot(xs, ys)
        return fig

    # Checks to see if token is valid and gets a new token if not
    def get_token(session):
        token_valid = False
        token_info = session.get("token_info", {})

        #print("hereg1")

        # Checking if the session already has a token stored
        if not (session.get('token_info', False)):

            print("hereg2")
            token_valid = False
            return token_info, token_valid

        #print("hereg3")



        # Checking if token has expired
        now = int(time.time())
        is_token_expired = session.get('token_info').get('expires_at') - now < 60



        # Refreshing token if it has expired
        if (is_token_expired):
            # print("here2g4")
            # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
            sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = CLI_ID, client_secret = CLI_SEC, redirect_uri = REDIRECT_URI, scope = SCOPE)
            token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

        token_valid = True
        return token_info, token_valid

    return app