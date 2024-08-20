import requests,os
import json
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv('API_KEY')
BASE_URL = 'https://api.themoviedb.org/3'

def get_trending_movies():
    url = f'{BASE_URL}/trending/movie/week?api_key={API_KEY}'
    response = requests.get(url)
    return response.json().get('results', [])

def get_movie_details(movie_id):
    url = f'{BASE_URL}/movie/{movie_id}?api_key={API_KEY}&append_to_response=credits'
    response = requests.get(url)
    return response.json()

def get_movie_providers(movie_id):
    url = f'{BASE_URL}/movie/{movie_id}/watch/providers?api_key={API_KEY}'
    response = requests.get(url)
    return response.json().get('results', {})

def main():
    trending_movies = get_trending_movies()
    # print(trending_movies)
    
    movie_data = []

    for movie in trending_movies[:]:  # Limiting to 5 trending movies for brevity
        movie_id = movie['id']
        movie_title = movie['title']
        movie_details = get_movie_details(movie_id)
        movie_providers = get_movie_providers(movie_id)
        
        # Get cast members
        cast = [actor['name'] for actor in movie_details.get('credits', {}).get('cast', [])][:5]  # Limit to top 5 actors
        
        # Get platforms where the movie is available
        platforms = []
        if 'IN' in movie_providers:  # Assuming US region, can be changed based on your location
            platforms = [provider['provider_name'] for provider in movie_providers['IN'].get('flatrate', [])]

        # Store data in dictionary format
        movie_info = {
            'Title': movie_title,
            'Release Date': movie_details.get('release_date'),
            'Cast': cast,
            'Available on': platforms if platforms else 'No platform information available'
        }

        movie_data.append(movie_info)
    
    # Write the data to a JSON file with ensure_ascii=False to handle special characters
    with open('data/Movie/trending_movies.json', 'w', encoding='utf-8') as json_file:
        json.dump(movie_data, json_file, ensure_ascii=False, indent=4)

    print("Data has been successfully written to trending_movies.json")

if __name__ == '__main__':
    main()
