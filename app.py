from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
from graph import Graph

# load enviornment variables
load_dotenv()

app = Flask(__name__)

graph = Graph() # init the graph

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
    
    # create graph node for the result
    node_id = result["id"]
    node_data = result["name"]

    # add node to graph
    graph.add_node(node_id, node_data)

    # relationships
    if search_type == 'artist':
        relationships = []
        if 'albums' in result:
            for album in result['albums']['items']:
                graph.add_node(album['id'], album['name'])  # add album as node
                relationships.append((node_id, album['id']))  # add relationship (edge) between artist and album
            
        # Add other relationships (e.g., artist to genres)
        graph.add_data_with_relationships({node_id: node_data}, relationships)

    elif search_type == 'album':
        relationships = []
        if 'tracks' in result:
            for track in result['tracks']['items']:
                graph.add_node(track['id'], track['name'])  # add song as a node
                relationships.append((node_id, track['id']))  # add relationship (edge) between album and song
        
        graph.add_data_with_relationships({node_id: node_data}, relationships)

    # No relationships for songs as they are leaf nodes

    return jsonify({
        'name': result['name'],
        'id': result['id'],
        'type': search_type,
        'extra_info': result.get('genres') if search_type == 'artist' else result.get('release_date')
    })


@app.route('/get_graph_data')
def get_graph_data():
    nodes = [{"id": node_id, "data": node_data} for node_id, node_data in graph.nodes.items()]
    edges = [{"source": node_id1, "target": node_id2} for node_id1, neighbors in graph.edges.items() for node_id2, _ in neighbors]

    return jsonify({
        "nodes": nodes,
        "edges": edges
    })


if __name__ == '__main__':
    app.run(debug=True)