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



# # import requests
# # import json

# # def fetch_products_from_makeup_api(gpt_recommendations):
# #     # The base URL for the Makeup API
# #     api_base_url = "http://makeup-api.herokuapp.com/api/v1/products.json"
    
# #     # Initialize a list to hold the recommended products
# #     products = []

# #     # Parse the GPT recommendations for brand and product type
# #     # Assuming the GPT response is in the following format:
# #     # [
# #     #     {"name": "Product Name", "brand": "Brand Name", "product_type": "Product Type"}
# #     # ]
# #     try:
# #         recommendations = json.loads(gpt_recommendations)

# #         # Loop through each recommendation and fetch from Makeup API
# #         for rec in recommendations:
# #             brand = rec.get("brand", "").lower()  # Get the brand from GPT response
# #             product_type = rec.get("product_type", "").lower()  # Get the product type from GPT response
            
# #             if brand and product_type:
# #                 # Make the request to the Makeup API
# #                 response = requests.get(f"{api_base_url}?brand={brand}&product_type={product_type}")
                
# #                 if response.status_code == 200:
# #                     product_data = response.json()
                    
# #                     # If there are products in the response, add the first one to the list
# #                     if product_data:
# #                         products.append({
# #                             "name": product_data[0].get("name"),
# #                             "brand": product_data[0].get("brand"),
# #                             "image": product_data[0].get("image_link"),  # The image URL from the API
# #                             "url": product_data[0].get("product_link"),  # The product page link
# #                             "price": product_data[0].get("price")
# #                         })
# #                 else:
# #                     print(f"Failed to fetch products for {brand} - {product_type}")
# #             else:
# #                 print(f"Missing brand or product type in GPT recommendation: {rec}")
    
# #     except json.JSONDecodeError as e:
# #         print(f"Error parsing GPT recommendations: {e}")

# #     return products


# from selenium import webdriver
# from selenium_stealth import stealth
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from bs4 import BeautifulSoup
# import time
# import json
# from selenium.common.exceptions import TimeoutException, NoSuchElementException

# def init_webdriver():
#     driver = webdriver.Chrome()
#     stealth(driver,
#             platform="Win32",
#             languages=["en-US", "en"],
#             vendor="Google Inc.",
#             webgl_vendor="Intel Inc.",
#             renderer="Intel Iris OpenGL Engine",
#             fix_hairline=True)
#     return driver

# try:
#     driver = init_webdriver()
#     driver.maximize_window()
#     driver.get('https://distore.one/')
#     time.sleep(1)

  
#     button_kozha = WebDriverWait(driver, 10).until(
#         EC.element_to_be_clickable((By.CSS_SELECTOR, "ul.elementor-icon-list-items li:nth-child(3) a"))
#     )

   
#     button_kozha.click()

#     time.sleep(1)
    
#     cnt = 0
#     products = []  
    
   
#     for i in range(60): 
#         try:
#             cnt += 1
#             print(f"Сбор данных со страницы {cnt}")
            
      
#             html_content = driver.page_source
#             soup = BeautifulSoup(html_content, 'html.parser')
#             product_divs = soup.find_all('div', class_='product-block')

#             if product_divs:
#                 print(f"Найдено {len(product_divs)} элементов на странице {cnt}.")
#             else:
#                 print("Элементы не найдены.")
#                 break  

   
#             for product_div in product_divs:
#                 product = {}
                
           
#                 title_tag = product_div.find('h3', class_='name')
#                 if title_tag and title_tag.find('a'):
#                     product['title'] = title_tag.find('a').text.strip()
#                     product['link'] = title_tag.find('a')['href']
                
                
#                 price_tag = product_div.find('span', class_='woocommerce-Price-amount')
#                 if price_tag:
#                     product['price'] = price_tag.text.strip()

              
#                 images = []
#                 image_tags = product_div.find_all('img', class_='item-slider')
#                 for img in image_tags:
#                     images.append(img['src'])
                
#                 product['images'] = images
                
               
#                 products.append(product)

          
#             next_button = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, 'a.next.page-numbers'))
#             )

            
#             if next_button.is_displayed() and next_button.get_attribute("href"):
#                 next_page_url = next_button.get_attribute("href")
#                 print(f"Переход на страницу: {next_page_url}")
                
                
#                 next_button.click()
#                 time.sleep(2)  

#             else:
#                 print("Конец пагинации достигнут или кнопка не активна.")
#                 break

#         except (TimeoutException, NoSuchElementException) as ex:
#             print(f"Ошибка при поиске кнопки 'Следующая страница': {ex}")
#             break  #


#     with open('aruuke.json', 'w', encoding='utf-8') as jsonfile:
#         json.dump(products, jsonfile, ensure_ascii=False, indent=4)
#     print("Данные сохранены в 'aruuke.json'")

# except Exception as ex:
#     print(f"Произошла ошибка: {ex}")

# finally:
#     driver.close()
#     driver.quit()

