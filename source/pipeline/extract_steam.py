"""Script which gets data from steam web api"""
from os import environ
import requests
import multiprocessing
import time
import json

URL_FORMAT = "https://store.steampowered.com/api/appdetails/?appids={appid}&cc=uk"
# WISHLIST_URL_FORMAT = "https://api.steampowered.com/IWishlistService/GetWishlist/v1/?access_token={api_key}&steamid={steamid}"
MAX_RESULTS = 10000
NUM_PROCESSES = 32


def get_from_steam_db(appid: int) -> dict:
    """Pull games, ids, and prices from database"""
    response = requests.get(URL_FORMAT.format(appid=appid))
    return response.json().get(str(appid))


def is_valid_steam_endpoint(appid: int) -> bool:
    """Pull games, ids, and prices from database"""
    response = requests.get(URL_FORMAT.format(appid=appid))
    return response.json().get(str(appid)).get('success')

# def get_wishlist_by_id(steamid: int) -> list[dict]:
#     response = requests.get(WISHLIST_URL_FORMAT.format(
#         api_key=environ['API_KEY'], steamid=steamid))
#     print(response.json())


def check_new_endpoints() -> int:
    app_id = 10
    failures = 100
    while failures > 0:
        try:
            if is_valid_steam_endpoint(app_id):
                failures -= 1
            app_id += 10
        except:
            continue

    print("no more results")
    print(f"last app id = {app_id}")

    return app_id


def get_game_data() -> list[dict]:
    """extract from public steam api"""
    response = requests.get(URL_FORMAT.format(appid=10))
    return response.json().get('10')


if __name__ == "__main__":
    start_time = time.time()
    # get_from_steam_db(1931180)
    # get_wishlist_by_id(76561199511570728)
    # with open("a_file.json", 'w', encoding='utf-8') as f:
    #     json.dump(get_game_info(), f, indent=4)
    print(get_game_data().get('data').get('name'))
    print(check_new_endpoints())

    end_time = time.time()
    print(f"Time taken: {end_time - start_time}")
