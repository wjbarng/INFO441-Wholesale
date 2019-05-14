This is a repository for INFO441 Wholesale Project

Database design: https://www.lucidchart.com/invitations/accept/86a6aaec-9d89-46e2-b6ab-ee0a94e94589

#Database
The database contains individual tables like Seller to record admin information and 
BusinessApplication to store applications for businesses that want to be members of
our wholesale store. In addition, the Customers database is linked one to one with the 
Django user database to keep track of individual members of the wholesale store. Each
customer can be linked to a payment method table. A shipping address table and order table
is linked by a foreign key to the customer table. Each order is linked by a foreign key to
a shipping method table.

1. application/
* Post: If given a valid form, a new application is saved in model BusinessApplication
        , a success message is shown, and user is redirected to the home page. If form 
        is not valid, an error message is shown and user remains on application page. Anyone
        can use the route. The field business name, address, zip, city, state, email, and 
        phone are saved in the model.
* Delete: Given a json object with a business name field, the application with the given business name
          is deleted from the BusinessApplication model. Responds with a HttpResponse of delete successful
          if application with given name is found. Wil respond with status code 400 if request cannot be encoded
          into json or status code 404 if application is not found. Responds with 200 status code if application is deleted.
* Get: Renders the business application form

2. shipping/
* Post: Can only be accessed if user is authenticated. If form is not valid, an error message will show and the
        user remains on the account page. If the form is valid, the shipping address information is saved in the
        ShippingAddress model. A success message will show and the account page will populate with the shipping info.
* Get: Renders the account page
* Delete: If the user is authenticated, this endpoint will delete all shipping addresses associated with the user.
          Returns with status code 200 if delete is successful. If no addresses are found, it responds with a 404
          status code.
