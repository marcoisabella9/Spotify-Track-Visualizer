# Spotify Data Visualizer
A tool for users to see connections in metadata from Spotify using their public API.
<br>
<br>
<h2>Background</h2>
The Spotify Data Visualizer is a tool that allows users to submit data (artists, tracks, albums) which then have their relationships visualized using a graph data structure. 
This project utilizes the public Spotify API to access their services and allows us to fetch this data as if the user were using the app themselves. 
This visualization can be helpful to users as it can help them interpret their music taste in new ways and possibly discover new music they could be interested in. 
The project itself is a HTML page that utilizes Flask for a python backend. 
The relationship based connections also have the possibility of becoming the beginnings of a user recommendation system, getting an idea for the users tastes and recommending them appropriate suggestions. 
The initial idea behind the project was to create a tool in which users could easily see connections between the data of their favorite music on Spotify. 
We planned for all types of information to be generated based on the data given but decided it was best to limit the scope to just artists, albums, and songs. 
We wanted it to be interactive and have a natural feel in adding data and viewing the connections. 
<h2>Design/Implementation</h2>
We chose to implement a graph data structure to contain the data. In order to visualize connections between data an obvious choice would be to use a tree or graph structure, as data could be represented as nodes and the connections between them could be the edges. 
Thinking further, we wanted our program to be free flowing and dictated by the searches of the user, who would also be able to move around and freely view those connections. 
This lead us to choose a graph structure over a tree because we wouldn’t want a root node for nodes to be based on, but rather free flowing nodes that could connect independently. 
The page requires the user to have installed both flask and dotenv onto their device. 
Flask is used as the web development framework with python and dotenv is used to load the API key from Spotify from the .env file. 
The user is also expected to have data from Spotify in mind to search for. 
The software has three main files, being index.html, app.py and the graph.py class. Index.html handles the D3.js functionality as well as the page formatting. 
The D3.js script uses the library to render a graph onto the page that represents the graph structure. The library contains all types of tools that we use to simulate a free flowing interactive graph. 
These tools include a force simulation that lets us have nodes automatically repel from each other, drag the nodes and have the graph react to that user input, zoom in and move the view around, have the nodes be represented by images, as well as other features.  
Graph.py is the graph class which is the backbone of the software. The graph is used to store all the information the user searches for and creates edges based on the relationships found in the app. 
It allows adding nodes, edges, and adding more data based on relationships with respective edges. 
App.py is the most expansive of the files, as it handles all interactions with the Spotify API, as well as utilizing the graph class in conjunction with the newfound data. 
It initially uses dotenv to import the .env files, as they are sensitive and should not be included in public releases. It also creates the web app with the Flask framework. 
It has multiple functions responsible for connecting to the Spotify API like retrieving the token, which uses the .env variables. This token is required to be passed whenever we try to perform an action that needs to reference the Spotify API, like searching. 
There are some more functions that retrieve relevant data from the search, like get_albums_by_artist(), and get_songs_from_album().  
Getting the token for the API can be performed in O(1) time as it simply refers the .env variables to Spotify to retrieve the token. 
The functions that handle searching for songs, albums, and artists can all also be performed in O(1) for similar reasons. 
Getting the relevant relationship info from these searches is a bit more complex however. 
These functions are performed in O(n) time with n representing the number of data found as each artist can have a different number of albums and each album can have a different number of songs. 
get_graph_data() can be performed in O(n + e) with n representing the number of nodes and e representing the number of edges. 
The main search function has to reference all the related nodes. 
This can be performed in O(1) + O(k) with O(1) being the search itself and then k being the number of relationships that have to be performed. 
<br>
<h2>Reflection</h2>
The Spotify Data Visualizer successfully allows users to interactively explore relationships between songs, albums, and artists using graph-based visualization. 
A shortcoming of this application is that it is limited to the faults of the Spotify API itself. Spotify’s metadata relies on the artist themself choosing to include it. 
This leads to the metadata not always being the most accurate. For example, “hidden features” where an artist featuring on another's song is not listed in the title or the metadata have become fairly common in music today. 
While this may provide a unique first-time listening experience it hinders our application as it can lead to confusion on why an artist may not connect to a node the user knows they feature on. 
Also there is the matter in which some artists put the feature in the title and not in the actual metadata. 
Artists also fairly often release a single under an album of the same name featuring only that one song. 
This is one of the main reasons I wanted to include multiple different node icons for data type as this can lead to seeing what appears to be the same node twice. 
This project also has the potential to expand into a user recommendation system, showcasing its versatility and value.  
