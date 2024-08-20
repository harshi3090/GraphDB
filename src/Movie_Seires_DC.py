import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv('API_KEY')
BASE_URL = 'https://api.themoviedb.org/3'

def get_trending_content(content_type='movie', count=10):
    url = f'{BASE_URL}/trending/{content_type}/week?api_key={API_KEY}'
    response = requests.get(url)
    return response.json().get('results', [])[:count]

def get_movie_details(movie_id):
    url = f'{BASE_URL}/movie/{movie_id}?api_key={API_KEY}&append_to_response=credits'
    response = requests.get(url)
    return response.json()

def get_tv_details(tv_id):
    url = f'{BASE_URL}/tv/{tv_id}?api_key={API_KEY}&append_to_response=credits'
    response = requests.get(url)
    return response.json()

def get_content_providers(content_id, content_type='movie', region='IN'):
    url = f'{BASE_URL}/{content_type}/{content_id}/watch/providers?api_key={API_KEY}'
    response = requests.get(url)
    return response.json().get('results', {}).get(region, {}).get('flatrate', [])

def get_genres(genre_ids, all_genres):
    return [genre['name'] for genre in all_genres if genre['id'] in genre_ids]

def save_content_to_json(content, filename):
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(content, json_file, ensure_ascii=False, indent=4)
    print(f"Data has been successfully written to {filename}")

def main():
    content_types = ['movie', 'tv']  # Handle both movies and TV series
    region = 'IN'
    count = 10 

    os.makedirs('data', exist_ok=True)

    # Get all genres for both movies and TV series
    movie_genres_url = f'{BASE_URL}/genre/movie/list?api_key={API_KEY}'
    tv_genres_url = f'{BASE_URL}/genre/tv/list?api_key={API_KEY}'

    movie_genres = requests.get(movie_genres_url).json().get('genres', [])
    tv_genres = requests.get(tv_genres_url).json().get('genres', [])

    for content_type in content_types:
        trending_content = get_trending_content(content_type, count)
        content_data = []

        for content in trending_content:
            content_id = content['id']
            content_title = content['title'] if content_type == 'movie' else content['name']
            content_details = get_movie_details(content_id) if content_type == 'movie' else get_tv_details(content_id)
            content_providers = get_content_providers(content_id, content_type, region)
            
            # Get cast members
            cast = [actor['name'] for actor in content_details.get('credits', {}).get('cast', [])][::]
            
            # Get platforms where the content is available
            platforms = [provider['provider_name'] for provider in content_providers]

            # Get language
            language = content_details.get('original_language')

            # Get genres
            genre_ids = content_details.get('genres', [])
            genres = get_genres([genre['id'] for genre in genre_ids], movie_genres if content_type == 'movie' else tv_genres)

            # Get overview
            overview = content_details.get('overview')

            # Store data in dictionary format
            content_info = {
                'Title': content_title,
                'Release Date': content_details.get('release_date') if content_type == 'movie' else content_details.get('first_air_date'),
                'Language': language,
                'Genres': genres,
                'Overview': overview,
                'Cast': cast,
                'Available on': platforms if platforms else ''
            }

            content_data.append(content_info)
        
        # Save each content type (movies and TV series) to a separate JSON file
        filename = f'data/Movie-Series/trending_{content_type}.json'
        save_content_to_json(content_data, filename)

if __name__ == '__main__':
    main()
