This is a repository for INFO441 Wholesale Project

Database design: https://www.lucidchart.com/invitations/accept/86a6aaec-9d89-46e2-b6ab-ee0a94e94589


# Database
The database an individual table
BusinessApplication to store applications for businesses that want to be members of
our wholesale store. In addition, the Customers database is linked one to one with the
Django user database to keep track of individual members of the wholesale store. Each
customer can be linked to a payment method table. A shipping address table and order table
is linked by a foreign key to the customer table. Each order is linked by a foreign key to
a shipping method table. Order table and products table are in a many to many relationship, so the product order table acts as an associative table. Each product is linked to a category so products table has a foreign key to category. Lastly, each product has one or more discounts and each discount can have one or more products, so these two tables are connected by a product discount table.

1. web_scraping view: scrapes product from Walmart and inserts into database
2. homepage: Renders homepage with scraped data of reasons to buy wholesale scraped from other site
3. default_category: Inserts categories into database if they have not been inserted
4. default_shipping: Inserts shipping methods into database if they have not been inserted
5. products: On get, renders all products for a given category
6. categories: On get, renders all categories
7. product_detail:
8. product_regi:
9. cart:
* Get: Renders the cart page with payment, shipping, items, discount, shipping, and total price shown
* Post: Takes payment, shipping, customer, item, price, and date information and inserts them into order database to create a new order
* Delete: Deletes item from cart table and cart page
10. about: renders about page
11. support: renders support page
12. application/
* Post: If given a valid form, a new application is saved in model BusinessApplication
        , a success message is shown, and user is redirected to the home page. If form
        is not valid, an error message is shown and user remains on application page. Anyone
        can use the route. The field business name, address, zip, city, state, email, and
        phone are saved in the model.
* Get: Renders the business application form
13. account: If the user is authenticated, the user's account information is rendered
14. shipping: If the user is authenticated, the following methods are accessible
* Get: Renders shipping address information for the user
* Post: Updates the shipping address for the user, if the user is an individual the first and last name are saved, if the user is a retailer, the business name is saved
15. payment: If the user is authenticated, the following methods are accessible
* Get: Shows the payment information for the user
* Post: Updates cardnumber and card name for user
16: order: If user is authenticated, a history of user's orders will be shown
17. signin: 
* Get: Returns the signin page
* Post: Signs the user in
18. signout: Signs out the user
19. register: 
* Post: Creates a new user
* Get: Return the register page
20. Category_view
21. Category_detail_view
22. Discount_view
23. Product_view
24. Product_detail_view


         




API Endpoints

\` = required

For the "POST", "DELETE", "PATCH" methods, users who are signed as ADMIN have permission.
For the "GET" method, anyone can call this method even people who are not signed in.

1. api/dicounts
  * "GET" = Displays the list of the discounts that Wholesale offers
  * "POST" = add new data into the Database
    * percentage = percentage of discount`
    * minQuan = minimum quantity`
    * maxQuan = maximum quantity`
    * id = id of the product`

    Returns the Json object with new data
  * "PATCH" = edit the existing data
    * id = id of the discount`
    * percentage = percentage of discount
    * minQuan = minimum quantity
    * maxQuan = maximum quantity

    Returns the Json object with updated data
    
  * "DELETE" = deleting the existing data
    * id = id of the product

2. api/categories
  * "GET" = Displays the list of the categories
  * "POST" = add new Categories into the Database
    * name = name of the category`
    * image = image of the category`

3. api/categories/<category_id>
  * "GET" = displays specific category with the products in the category
  * "PATCH" = updates data of specific category
    * name = name of the category
    * image = image of the category`
  * "DELETE" = delete the category

Following fields are stored in the category table as a defualt values.
* Pantry & Dry Goods
* Bath & Facial Tissue
* Canned Goods
* Cleaning Products
* Coffee & Sweeteners
* Emergency Kits & Supplies
* Breakroom Serving Supplies
* Gourmet Foods
* Paper Towels
* Snacks
* Water & Beverages

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
