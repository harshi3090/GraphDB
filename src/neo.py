from neo4j import GraphDatabase
import json

uri = "bolt://localhost:7687"
user = "neo4j"
password = "password"  
driver = GraphDatabase.driver(uri, auth=(user, password))

# Function to create nodes and relationships for a movie
def create_movie_graph(tx, movie):
    title = movie['Title']
    release_date = movie['Release Date']
    language = movie['Language']
    genres = movie['Genres']
    overview = movie['Overview']
    cast = movie['Cast']
    platforms = movie['Available on']
    
    # Create Movie node
    tx.run(
        """
        MERGE (m:Movie {title: $title})
        SET m.release_date = $release_date, m.overview = $overview
        """,
        title=title, release_date=release_date, overview=overview)
    
    # Create Language node and relationship
    tx.run(
        """
        MERGE (l:Language {name: $language})
        MERGE (m:Movie {title: $title})-[:RELEASED_IN]->(l)
        """,
        language=language, title=title)
    
    # Create Genre nodes and relationships
    for genre in genres:
        tx.run(
            """
            MERGE (g:Genre {name: $genre})
            MERGE (m:Movie {title: $title})-[:HAS_GENRE]->(g)
            MERGE (g)-[:HAS_MOVIE]->(m)
            """,
            genre=genre, title=title)
    
    # Create Cast nodes, relationships and update Actor-Movie relationship
    for actor in cast:
        tx.run(
            """
            MERGE (a:Actor {name: $actor})
            MERGE (m:Movie {title: $title})-[:HAS_CAST]->(a)
            MERGE (a)-[:ACTED_IN]->(m)
            """,
            actor=actor, title=title)
    
    # Create Platform nodes and relationships
    for platform in platforms:
        tx.run(
            """
            MERGE (p:Platform {name: $platform})
            MERGE (m:Movie {title: $title})-[:AVAILABLE_ON]->(p)
            MERGE (p)-[:HAVE_MOVIES]->(m)
            """,
            platform=platform, title=title)

data_file = r"data/Movie-Series/trending_tv.json"
with open(data_file, 'r', encoding='utf-8') as f:
    data = json.load(f)


with driver.session() as session:
    for movie in data:
        session.execute_write(create_movie_graph, movie)

driver.close()