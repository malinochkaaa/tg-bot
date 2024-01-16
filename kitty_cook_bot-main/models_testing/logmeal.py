import requests
from pathlib import Path

API_USER_TOKEN = 'db88dae74468552565ccdf4657e23be339989b80'

# for food location search
def dish_recognition(img_path: str):
    headers = {'Authorization': 'Bearer ' + API_USER_TOKEN}

    # Single/Several Dishes Detection
    url = 'https://api.logmeal.es/v2/image/segmentation/complete'
    resp = requests.post(url,files={'image': open(img_path, 'rb')}, headers=headers)
    return resp.json()['segmentation_results'][0]['recognition_results'][0]['name']


# for food search and nutrition analysis
def nutritional_info(img_path: str):
    headers = {'Authorization': 'Bearer ' + API_USER_TOKEN}

    # Single/Several Dishes Detection
    url = 'https://api.logmeal.es/v2/image/segmentation/complete'
    resp = requests.post(url, files={'image': open(img_path, 'rb')}, headers=headers)

    # Nutritional information
    url = 'https://api.logmeal.es/v2/recipe/nutritionalInfo'
    resp = requests.post(url, json={'imageId': resp.json()['imageId']}, headers=headers)
    return resp.json()


if __name__ == '__main__':
    img_path = Path('food_img/apple.jpg')
    
    print('Test Nutrition')
    info = nutritional_info(img_path)
    print(info['foodName'][0])
    print(info['nutritional_info'])

    # print('Test Dish')
    # dish = dish_recognition(img_path)
    # print(dish)
