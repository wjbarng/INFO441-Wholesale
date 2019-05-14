This is a repository for INFO441 Wholesale Project

Database design: https://www.lucidchart.com/invitations/accept/86a6aaec-9d89-46e2-b6ab-ee0a94e94589

Pages

Endpoints

\` = required

1. api/dicounts
  * "GET" = Displays the list of the discounts that Wholesale offers
  * "POST" = add new data into the Database
    * percentage = percentage of discount`
    * minQuan = minimum quantity`
    * maxQuan = maximum quantity`
    * disShipping = dicount on disShipping`

    Returns the Json object with new data
  * "PATCH" = edit the existing data
    * id = id of the discount`
    * percentage = percentage of discount
    * minQuan = minimum quantity
    * maxQuan = maximum quantity
    * disShipping = dicount on disShipping

    Returns the Json object with updated data

2. api/categories
  * "GET" = Displays the list of the categories
  * "POST" = add new Categories into the Database
    * name = name of the category'
    * description = description of the category
    * image = image of the category`

3. api/categories/<category_id>
  * "GET" = displays specific category with the products in the category
  * "PATCH" = updates data of specific category
    * name = name of the category
    * description = description of the category
    * image = image of the category`
  * "DELETE" = delete the category

4. api/products
  * "GET" = displays the list of the products
  * "POST" = Adds new product into the Database
    * name = name of the product`
    * description = description of the product
    * image = image
    * price = price`
    * category = category name`
    * max_quantity = max quantity that one order can buy`
    * min_quantity_retail = min quantity that one retailer should buy`
    return the new data in the JSON Format
  * "DELETE" = delete the product from the database
    * name = name of the product


5. api/products/<product_id>
  * "GET" = displays the product information
  * "PATCH" = update the product information
    * name = name of the product
    * description = description of the product
    * image = image
    * price = price
    * max_quantity = max quantity that one order can buy
    * min_quantity_retail = min quantity that one retailer should buy
    returns the updated JSON data
