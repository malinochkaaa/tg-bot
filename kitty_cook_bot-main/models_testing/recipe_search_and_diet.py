import requests
from pathlib import Path


IMAGE_PATH = Path('./recipe_search_and_diet/images')


def recipe_search(dish: str):
    url = "https://edamam-recipe-search.p.rapidapi.com/search"

    querystring = {'q' : dish}

    headers = {
        "X-RapidAPI-Key": "29aeea59e0msh98b825c854dcf76p1334b3jsn40fe758d4886",
        "X-RapidAPI-Host": "edamam-recipe-search.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    return response.json()


def save_image(url: str, save_name: str):
    img_data = requests.get(url).content
    with open(IMAGE_PATH / f'{save_name}.jpg', 'wb') as handler:
        handler.write(img_data)


if __name__ == '__main__':
    IMAGE_PATH.mkdir(parents=True, exist_ok=True)

    recipe = recipe_search('apple')
    print(len(recipe['hits']))

    image_name = recipe['hits'][0]['recipe']['label']
    print(image_name)

    image_url = recipe['hits'][0]['recipe']['image']
    save_image(image_url, 'image_name')

    total_nutrients = recipe['hits'][0]['recipe']['totalNutrients']
    total_daily = recipe['hits'][0]['recipe']['totalDaily']
    
    print(total_nutrients) # граммовки веществ с блюда
    print(total_daily) # процент веществ на день с блюда