"""Script which scrapes data from Epic Games DB"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from epicstore_api import EpicGamesStoreAPI
import threading

api = EpicGamesStoreAPI()
lock = threading.Lock()


def fetch_game(slug, namespace):
    """Fetch a single game and return data"""
    try:
        product = api.get_product(slug)

        title = product.get("title")
        pages = product.get("pages", [])

        first_offer = None
        for page in pages:
            offer = page.get("offer")
            if offer and offer.get("id"):
                first_offer = (page["namespace"], offer["id"])
                break

        retail_price = 0
        discount_price = 0
        game_id = None
        namespace_final = namespace

        if first_offer:
            offer_ns, offer_id = first_offer

            offer_data = api.get_offers_data(
                api.OfferData(offer_ns, offer_id))[0]
            catalog = offer_data["data"]["Catalog"]["catalogOffer"]

            game_id = catalog.get("id")
            namespace_final = catalog.get("namespace")

            price = catalog.get("price", {}).get("totalPrice", {})

            retail_price = price.get("originalPrice", 0)
            discount_price = price.get("discountPrice", 0)
        else:
            game_id = product.get("id") or slug
            namespace_final = product.get("namespace") or namespace

            prod_price = product.get("price", {})
            total_price = prod_price.get("totalPrice") or {}

            retail_price = total_price.get("originalPrice") or 0
            discount_price = total_price.get("discountPrice") or 0

        return {
            "id": game_id,
            "title": title,
            "namespace": namespace_final,
            "slug": slug,
            "retailPrice": retail_price,
            "discountPrice": discount_price
        }

    except Exception as e:
        print(f"Error while processing {slug}: {e}")
        return None


def extract_epic_games(limit: int | None = None) -> list[dict]:
    """Extract all games and their prices from Epic Games Store"""

    api = EpicGamesStoreAPI()

    product_map = api.get_product_mapping()

    all_games = []
    count = 0

    for slug, namespace in product_map.items():
        if limit is not None and count >= limit:
            break

        try:
            product = api.get_product(slug)

            title = product.get("title")
            pages = product.get("pages", [])

            offer = next((page for page in pages if page.get(
                "offer") and page["offer"].get("id")), None)

            if not offer:
                continue

            offer_ns = offer["namespace"]
            offer_id = offer["offer"]["id"]

            offer_data = api.get_offers_data(
                api.OfferData(offer_ns, offer_id))[0]

            catalog_offer = offer_data["data"]["Catalog"]["catalogOffer"]
            price_info = catalog_offer.get("price", {}).get("totalPrice", {})

            all_games.append({
                "id": catalog_offer.get("id"),
                "title": title,
                "namespace": catalog_offer.get("namespace"),
                "slug": slug,
                "price_original": price_info.get("originalPrice"),
                "price_discount": price_info.get("discountPrice"),
                "currency": price_info.get("currencyCode")
            })

            count += 1

        except Exception:
            continue

    return all_games


if __name__ == "__main__":
    product_map = api.get_product_mapping()

    slug, namespace = next(iter(product_map.items()))

    print("Testing first game: ")
    print("Slug: ", slug)
    print("Namespace: ", namespace)
    print("-----------")

    result = fetch_game(slug, namespace)

    print("Result: ")
    print(result)
