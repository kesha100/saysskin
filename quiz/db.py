import os
import sys
import django
import requests
import logging
from dotenv import load_dotenv

# Get the project root directory (where manage.py is located)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "says.settings")
django.setup()

# Now you can import your Django models
from quiz.models import SephoraProduct

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def fetch_sephora_products():
    url = "https://sephora.p.rapidapi.com/products/list"
    headers = {
        "x-rapidapi-key": os.getenv('RAPIDAPI_KEY'),
        "x-rapidapi-host": "sephora.p.rapidapi.com"
    }
    
    categories = {
        "cleanser": "cat60104",
        "toner": "cat1230036",
        "moisturizer": "cat60208",
        "sunscreen": "cat150006"
    }
    
    all_products = []
    
    for category, category_id in categories.items():
        logger.info(f"Fetching {category} products...")
        querystring = {"categoryId": category_id, "pageSize": "100", "currentPage": "1"}
        try:
            response = requests.get(url, headers=headers, params=querystring)
            response.raise_for_status()
            
            products = response.json().get('products', [])
            logger.info(f"Fetched {len(products)} {category} products")
            
            for product in products:
                try:
                    SephoraProduct.objects.update_or_create(
                        product_id=product['productId'],
                        defaults={
                            'name': product['displayName'],
                            'brand': product['brandName'],
                            'category': category,
                            'price': product.get('currentSku', {}).get('listPrice'),
                            'image_url': product.get('heroImage', ''),
                            'product_url': f"https://www.sephora.com/product/{product['targetUrl']}"
                        }
                    )
                except Exception as e:
                    logger.error(f"Error saving product {product['productId']}: {str(e)}")
            
            all_products.extend(products)
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {category} products: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error while processing {category} products: {str(e)}")
    
    logger.info(f"Fetched and stored {len(all_products)} products from Sephora API")
    logger.info(f"Total products in database: {SephoraProduct.objects.count()}")

if __name__ == "__main__":
    logger.info("Starting to fetch Sephora products...")
    fetch_sephora_products()
    logger.info("Finished fetching Sephora products")