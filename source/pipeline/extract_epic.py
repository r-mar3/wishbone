"""Script which scrapes all games from Epic Games Store using GraphQL API directly"""
import requests
import json
import pprint

GRAPHQL_ENDPOINT = "https://graphql.epicgames.com/graphql"

STORE_QUERY = """
query searchStoreQuery(
  $allowCountries: String
  $category: String
  $count: Int
  $country: String!
  $keywords: String
  $locale: String
  $namespace: String
  $sortBy: String
  $sortDir: String
  $start: Int
  $withPrice: Boolean = true
) {
  Catalog {
    searchStore(
      allowCountries: $allowCountries
      category: $category
      count: $count
      country: $country
      keywords: $keywords
      locale: $locale
      namespace: $namespace
      sortBy: $sortBy
      sortDir: $sortDir
      start: $start
    ) {
      elements {
        title
        id
        namespace
        description
        productSlug
        urlSlug
        effectiveDate
        keyImages {
          type
          url
        }
        seller {
          id
          name
        }
        categories {
          path
        }
        price(country: $country) @include(if: $withPrice) {
          totalPrice {
            discountPrice
            originalPrice
            voucherDiscount
            discount
            currencyCode
            currencyInfo {
              decimals
            }
            fmtPrice(locale: $locale) {
              originalPrice
              discountPrice
              intermediatePrice
            }
          }
        }
      }
      paging {
        count
        total
      }
    }
  }
}
"""


def fetch_epic_games(country="GB", locale="en-GB", batch_size=1000):
    """Fetch all games from Epic Games Store using direct GraphQL queries"""
    
    all_games = []
    start = 0
    
    print(f"Fetching games from Epic Games Store ({country})...")
    
    while True:
        variables = {
            "allowCountries": country,
            "category": "games/edition/base|bundles/games|editors|software/edition/base",
            "count": batch_size,
            "country": country,
            "locale": locale,
            "namespace": "",
            "sortBy": "title",
            "sortDir": "ASC",
            "start": start,
            "withPrice": True
        }
        
        try:
            response = requests.post(
                GRAPHQL_ENDPOINT,
                json={
                    "query": STORE_QUERY,
                    "variables": variables
                },
                headers={
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching batch at start={start}: {e}")
            break
        except json.JSONDecodeError as e:
            print(f"JSON decode error at start={start}: {e}")
            print(f"Response text: {response.text[:500]}")
            break
        
        elements = data.get('data', {}).get('Catalog', {}).get('searchStore', {}).get('elements', [])
        paging = data.get('data', {}).get('Catalog', {}).get('searchStore', {}).get('paging', {})
        
        if not elements:
            print("No more games found.")
            break
        
        print(f"Fetched {len(elements)} games (total: {len(all_games) + len(elements)} / {paging.get('total', '?')})")
        
        for game in elements:
            price_data = game.get('price', {}).get('totalPrice', {})
            
            game_info = {
                'id': game.get('id'),
                'title': game.get('title'),
                'namespace': game.get('namespace'),
                'slug': game.get('productSlug') or game.get('urlSlug'),
                'description': game.get('description', ''),
                'seller': game.get('seller', {}).get('name', ''),
                'retailPrice': price_data.get('originalPrice', 0),
                'discountPrice': price_data.get('discountPrice', 0),
                'currencyCode': price_data.get('currencyCode', country),
                'discount': price_data.get('discount', 0),
                'onSale': price_data.get('discountPrice', 0) < price_data.get('originalPrice', 0),
                'effectiveDate': game.get('effectiveDate', '')
            }
            
            all_games.append(game_info)
        
        start += batch_size
        if len(elements) < batch_size:
            print("Reached end of catalog.")
            break
        
        if start > 50000:
            print("Reached safety limit (50,000 games)")
            break
    
    return all_games


def save_to_json(games, filename='epic_games.json'):
    """Save games list to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(games, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(games)} games to '{filename}'")


if __name__ == "__main__":
    print("=" * 70)
    print("Epic Games Store - Complete Catalog Scraper")
    print("=" * 70)
    
    # Fetch all games
    games = fetch_epic_games(country="GB", locale="en-GB")
    
    print("\n" + "=" * 70)
    print(f"Total games fetched: {len(games)}")
    
    if games:
        # Calculate statistics
        free_games = [g for g in games if g['retailPrice'] == 0]
        on_sale = [g for g in games if g['onSale']]
        paid_games = [g for g in games if g['retailPrice'] > 0]
        
        print(f"Free games: {len(free_games)}")
        print(f"Paid games: {len(paid_games)}")
        print(f"Games on sale: {len(on_sale)}")
        
        # Show sample
        print("\n" + "=" * 70)
        print("Sample games (first 5):")
        print("=" * 70)
        pprint.pprint(games[:5], width=100, compact=False)
        
        # Save to file
        print("\n" + "=" * 70)
        save_to_json(games)
    else:
        print("No games were fetched.")
