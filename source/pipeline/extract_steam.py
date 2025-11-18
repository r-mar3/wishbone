"""Script which gets data from steam web api"""
from os import environ
from dotenv import load_dotenv
import requests
import multiprocessing
import time
import json

URL_FORMAT = "https://store.steampowered.com/api/appdetails/?appids={appid}&cc=uk&filters=price_overview"
# WISHLIST_URL_FORMAT = "https://api.steampowered.com/IWishlistService/GetWishlist/v1/?access_token={api_key}&steamid={steamid}"
GAME_INFO_URL_FORMAT = "https://api.steampowered.com/IStoreService/GetAppList/v1/?access_token={api_key}&max_results={max_results}&last_appid={page_index}"
MAX_RESULTS = 10000
NUM_PROCESSES = 32


def get_from_steam_db(appid: int) -> dict:
    """Pull games, ids, and prices from database"""
    response = requests.get(URL_FORMAT.format(appid=appid))
    print(response.json())


# def get_wishlist_by_id(steamid: int) -> list[dict]:
#     response = requests.get(WISHLIST_URL_FORMAT.format(
#         api_key=environ['API_KEY'], steamid=steamid))
#     print(response.json())

def check_new_endpoints() -> int:
    is_more_results = True
    page_index = 0
    while is_more_results:
        response = requests.get(GAME_INFO_URL_FORMAT.format(
            api_key=environ['API_KEY'], max_results=MAX_RESULTS, page_index=page_index))
        output = response.json()
        is_more_results = output.get('response').get('have_more_results')
        if is_more_results:
            last_appid = output.get('response').get('last_appid')
            page_index = last_appid

    print("no more results")
    print(f"last app id = {last_appid}")

    return last_appid


def fetch_game_info_page(page_index: int) -> list[dict]:
    response = requests.get(
        GAME_INFO_URL_FORMAT.format(api_key=environ['API_KEY'], max_results=MAX_RESULTS, page_index=page_index))

    return response.json().get('response').get('apps')


def get_game_info() -> list[dict]:
    last_appid = check_new_endpoints()
    pages = range(0, last_appid, 100000)
    with multiprocessing.Pool(NUM_PROCESSES) as pool:
        output = pool.map(fetch_game_info_page, pages)

    return output


if __name__ == "__main__":
    start_time = time.time()
    load_dotenv()
    # get_from_steam_db(1931180)
    # get_wishlist_by_id(76561199511570728)
    with open("a_file.json", 'w', encoding='utf-8') as f:
        json.dump(get_game_info(), f, indent=4)

    end_time = time.time()
    print(f"Time taken: {end_time - start_time}")
