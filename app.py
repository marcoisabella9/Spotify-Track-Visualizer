from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
from graph import Graph

# Load environment variables
load_dotenv()

app = Flask(__name__, static_url_path='/images', static_folder='images')

graph = Graph()  # Initialize the graph

# Get client ID and client secret from .env file
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


# --- Spotify API Functions ---

# Retrieve token from the Spotify API
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


# Search for artist, returns only the top result
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


def get_albums_by_artist(token, artist_id):
    """
    Retrieves a list of albums for a given artist.
    """
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"include_groups": "album", "limit": 50}

    response = get(url, headers=headers, params=params)
    print("get_albums_by_artist Response:", response.status_code, response.content)

    if response.status_code != 200:
        raise ValueError(f"Failed to fetch albums for artist {artist_id}. Response: {response.json()}")

    albums_data = response.json().get("items", [])
    albums = [{"id": album["id"], "name": album["name"]} for album in albums_data]

    return albums


def get_songs_from_album(token, album_id):
    """
    Retrieves a list of songs (tracks) from a given album.
    """
    url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"limit": 50}

    response = get(url, headers=headers, params=params)
    print("get_songs_from_album Response:", response.status_code, response.content)

    if response.status_code != 200:
        raise ValueError(f"Failed to fetch songs for album {album_id}. Response: {response.json()}")

    songs_data = response.json().get("items", [])
    songs = [{"id": track["id"], "name": track["name"]} for track in songs_data]

    return songs


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_graph_data')
def get_graph_data():
    nodes = [{"id": node_id, "data": node_data} for node_id, node_data in graph.nodes.items()]
    edges = [{"source": node_id1, "target": node_id2} for node_id1, neighbors in graph.edges.items() for node_id2, _ in
             neighbors]

    # Debugging: Print nodes and edges for verification
    print("Nodes:", nodes)
    print("Edges:", edges)

    return jsonify({
        "nodes": nodes,
        "edges": edges
    })


@app.route('/search', methods=['POST'])
def search():
    search_query = request.form['search_query']
    search_type = request.form['search_type']
    token = get_token()

    # Fetch result based on type
    if search_type == 'artist':
        result = search_for_artist(token, search_query)
    elif search_type == 'album':
        result = search_for_album(token, search_query)
    elif search_type == 'song':
        result = search_for_song(token, search_query)
    else:
        return jsonify({'error': 'Invalid search type'})

    if not result:
        return jsonify({'error': f'{search_type.capitalize()} not found'})

    # Add the main entity as a node
    graph.add_node(result['id'], result['name'])

    # Add related entities and edges
    if search_type == 'song':
        # Extract album and featured artists
        album = result.get('album')
        featured_artists = result.get('artists', [])

        if album:
            graph.add_node(album['id'], album['name'])
            graph.add_edge(result['id'], album['id'])  # Song -> Album

        for artist in featured_artists:
            graph.add_node(artist['id'], artist['name'])
            graph.add_edge(result['id'], artist['id'])  # Song -> Artist

    elif search_type == 'album':
        # Add relationships for album's songs
        songs = get_songs_from_album(token, result['id'])
        for song in songs:
            graph.add_node(song['id'], song['name'])
            graph.add_edge(result['id'], song['id'])  # Album -> Song

    elif search_type == 'artist':
        # Add relationships for artist's albums
        albums = get_albums_by_artist(token, result['id'])
        for album in albums:
            graph.add_node(album['id'], album['name'])
            graph.add_edge(result['id'], album['id'])  # Artist -> Album

    return jsonify({'message': f'{search_type.capitalize()} "{result["name"]}" added to graph.'})


if __name__ == '__main__':
    app.run(debug=True)

