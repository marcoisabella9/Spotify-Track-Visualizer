from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json

# load enviornment variables
load_dotenv()

app = Flask(__name__, static_url_path='/images', static_folder='images')

# getting client id and client secret from .env file
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# ---spotify API functions---

# retrieving token from the spotify api
def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

# Search for artist, returns only top result
def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No artist with this name exists.")
        return None
    
    return json_result[0]

def search_for_album(token, album_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={album_name}&type=album&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["albums"]["items"]
    if len(json_result) == 0:
        print("No album with this name exists.")
        return None
    
    return json_result[0]

def search_for_song(token, song_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={song_name}&type=track&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["tracks"]["items"]
    if len(json_result) == 0:
        print("No song with this name exists.")
        return None
    
    return json_result[0]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    search_query = request.form['search_query']
    search_type = request.form['search_type']  # Can be 'artist', 'album', or 'song'
    token = get_token()

    if search_type == 'artist':
        result = search_for_artist(token, search_query)
    elif search_type == 'album':
        result = search_for_album(token, search_query)
    elif search_type == 'song':
        result = search_for_song(token, search_query)
    else:
        return jsonify({'error': 'Invalid search type'})

    if result is None:
        return jsonify({'error': f'{search_type.capitalize()} not found'})

    return jsonify({
        'name': result['name'],
        'id': result['id'],
        'type': search_type,
        'extra_info': result.get('genres') if search_type == 'artist' else result.get('release_date')
    })


if __name__ == '__main__':
    app.run(debug=True)
