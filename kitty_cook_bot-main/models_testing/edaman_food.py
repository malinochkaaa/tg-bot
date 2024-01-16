import requests


def search(food_name: str, measure: str):
    url = "https://edamam-edamam-nutrition-analysis.p.rapidapi.com/api/nutrition-data"

    querystring = {"ingr":f"1 {measure} {food_name}"}

    headers = {
        "X-RapidAPI-Key": "29aeea59e0msh98b825c854dcf76p1334b3jsn40fe758d4886",
        "X-RapidAPI-Host": "edamam-edamam-nutrition-analysis.p.rapidapi.com"
    }

    return requests.request("GET", url, headers=headers, params=querystring).json()


if __name__ == "__main__":
    print(search("apple", "large")["calories"])