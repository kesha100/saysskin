# # import http.client
# # import json

# # def fetch_products_by_keyword(gpt_recommendations):
# #     conn = http.client.HTTPSConnection("sephora14.p.rapidapi.com")

# #     headers = {
# #         'x-rapidapi-key': "57fefe12b4mshfb0af0d20659529p1b250cjsn5638464dc17e",
# #         'x-rapidapi-host': "sephora14.p.rapidapi.com"
# #     }

# #     products = []

# #     # Remove any extraneous formatting from GPT recommendations
# #     cleaned_recommendations = gpt_recommendations.replace("[", "").replace("]", "").replace("{", "").replace("}", "").split("\n")

# #     # Loop through each recommendation and search for products
# #     for recommendation in cleaned_recommendations:
# #         query = recommendation.strip().lower().replace(" ", "%20")  # Ensure the search term is URL-safe

# #         if query:  # Only proceed if the query is not empty
# #             conn.request("GET", f"/searchByKeyword?page=1&sortBy=NEW&search={query}", headers=headers)
# #             res = conn.getresponse()
# #             data = res.read()

# #             try:
# #                 sephora_products = json.loads(data.decode("utf-8"))
# #                 print(sephora_products)

# #                 # Check if 'data' key is present in the response
# #                 if 'data' in sephora_products:
# #                     for product in sephora_products['data']:
# #                         # Extract the relevant fields from each product
# #                         products.append({
# #                             "name": product.get('displayName'),
# #                             "image": product.get('altImage'),  # Assuming 'altImage' has the correct image
# #                             "url": product.get('targetUrl')
# #                         })
# #                 else:
# #                     print(f"No products found for recommendation: {recommendation}")

# #             except json.JSONDecodeError:
# #                 print(f"Error decoding JSON response for recommendation: {recommendation}")

# #     return products



#