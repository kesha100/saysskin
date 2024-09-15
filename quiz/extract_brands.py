# import json

# # Load your scraped JSON data from a file
# with open('aruuke.json', 'r', encoding='utf-8') as f:
#     products = json.load(f)

# # Function to extract the brand from the product title
# def extract_brand(title):
#     # Assuming the brand is the first word or first two words, depending on the format
#     # Customize this based on patterns you see in your data
#     brand = title.split()[0]  # First word as brand
#     return brand

# # Set to store unique brands
# unique_brands = set()

# # Loop through the products and extract brands
# for product in products:
#     title = product.get('title', '')
#     if title:
#         brand = extract_brand(title)
#         unique_brands.add(brand)

# # Convert the set to a sorted list for better readability
# unique_brands = sorted(unique_brands)

# # Save the unique brands to a new JSON file or print them
# with open('unique_brands.json', 'w', encoding='utf-8') as f:
#     json.dump(list(unique_brands), f, ensure_ascii=False, indent=4)

# print(f"Extracted {len(unique_brands)} unique brands:")
# print(unique_brands)
