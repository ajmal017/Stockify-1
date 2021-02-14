# Django Stocks Trading Platform
## Summary
Our site is a stocks trading platform that allows users to make trades in real time. Users can make trades for multiple companies in one order and the app uses real time stock data from the IEXCloud API. Web scraping is performed every time the search page is loaded to randomly generate select S&P500 companies and add them to the database.


## Definitions
Json input will be defined as:

    {
        "key": valueType (example value)
    }

For example,

    {
        "companyName" : String ("Amazon")
    }

Means a key of "companyName" has a String value Amazon

A "*" next to a key means it is optional

All defined HTTP methods throw missing parameter errors, user permissions errors, and missing object errors (e.g. trying to access a stock that doesn't exist throws an error)

If HTTP method executes successfully, it will return status code of 200. Missing objects will return 404. Missing parameters or incorrect user permissions return 400 and other methods will return the approriate status codes as needed.

# Endpoints

## Auth Views (auth/)

### "signin"
##### HTTP GET:
Renders the sign in page with a form for the username and password with status 200. 

##### HTTP POST:
Processes the sign in form data after the user clicks submit and checks to make sure the user is in the database to authenticate with status 200. Otherwise, an error message is shown with status 401.

##### Other HTTP Request Methods:
An error message is returned with status 405

### "register"
##### HTTP GET:
Renders the registration form for the user with status 200.

##### HTTP POST:
Processes the registration form after the submit button is pressed, and adds the user to the database with status 200. Checks for valid input as well as valid passwords. Invalid form entries will return status 400 and non matching passwords return status 400.

##### Other HTTP Request Methods:
An error message is returned with status 405

### "signout"
##### HTTP GET:
Signs the user out of their account if they are currently logged in with status 200, otherwise an error message is shown.

##### Other HTTP Request Methods:
An error message is returned with status 405

## Broker Views (/brokers) --
You can test the broker feature with these account credentials:
    user: testbroker
    pw: a

### "/"
##### HTTP GET:
Renders the brokerboard with status 200. Lists the customers currently managed by the broker.
Will return a 404 HTTPResponse if user/profile does not exist.

### "/\<int:customer_id\>
##### HTTP GET:
Renders the customer's profile and lists the customers recent orders with status 200.
Will redirect brokerboard with status 404 if user/profile does not exist.

### "buy/\<int:customer_id\>"
Same functionality as "/stocks/search"

### "orders/\<int:customer_id\>/\<int:order_id\>"
Same functionality as "/dashboard/orders/\<int:order_id\>"

## Dashboard Views (/dashboard)

### "/"
##### HTTP GET:
Renders the user's dashboard page with status code 200 and displays information such as recent orders, # of transactions, etc.  If the user is not logged in, the an error message is displayed along with status 401. 

##### Other HTTP Request Methods:
An error message is returned with status 405

### "company/\<int:company_id\>"

##### HTTP GET:
Renders the specified company info determined by the company id parameter supplied by the user. Returns a status code of 200 if successful. If the user is not authenticated, an error message is returned with status code 400.

##### Other HTTP Request Methods:
An error message is returned with status 405


### "company/\<str:company_name\>"

##### HTTP GET:
Renders the specified company info determined by the company name parameter supplied by the user. Returns a status code of 200 if successful. If the user is not authenticated, an error message is returned with status code 400.


##### HTTP PATCH:
Updates the company info only if the user is an admin and returns a JSON response with the newly updated company info.

Input:
    
    {
        *"manager_id": Integer
        "companyName": String ("Amazon")
        *"city": ("Seattle")
        *"region": String ("Snohomish")
        *"postalCode": Integer (98012)
        *"phone": String ("123-123-1231")
        *"homePage" : URL ("https://...")
    }

Output:

    {
        "company_id": 2, 
        "manager_id": 2, 
        "companyName": "Amazon", 
        "city": "Seattle", 
        "region": "Snohomish", 
        "postalCode": 98012, 
        "phone": "123-123-1231", 
        "homePage": "https://..."
    }

##### HTTP DELETE:
Deletes the specified company from database if the user is an admin and returns a message confirming the delete. 

Output:

    Delete was successful
    
    
##### Other HTTP Request Methods:
An error message is returned with status 405

### "orders"

##### HTTP GET:
Renders all of the orders for the specified user if they are logged in and displays in on the html template along with status code 200. If the user is not authenticated, then a message is returned along with status code 401.

##### HTTP POST:
Creates a new order for that specific user and returns a JSON response of the newly created order

Input:
    
    {
        *"order_id": Integer
        *"user_id": Integer
        "created_at": 2019-05-14
        "modified_at": 2019-05-14
    }

Output:

    {
        *"order_id": 1
        *"user_id": 1
        "created_at": 2019-05-14
        "modified_at": 2019-05-14
    }

##### HTTP PATCH:
Allows the user to release the order to someone else (transfer)

Input:
    
    {
        *"order_id": Integer
        *"user_id": Integer
    }

Output:

    {
        *"order_id": 2
        *"user_id": 5
        "created_at": 2019-05-14
        "modified_at": 2019-05-20
    } 
    
##### Other HTTP Request Methods:
An error message is returned with status 405
    
    
### "orders/<int:order_id>"

##### HTTP GET:
Returns the details of a specific order associated with that id along with status code 200. If the user is not authenticated, then a error message is returned with status code 401.

Output:

    {
        *"order_id": 1
        *"stock_id": 1
        unit_price: 3.99
        "quantity": 100
        "created_at": 2019-05-14
    }

##### HTTP POST:
Allows the user to sell the current order specified with the order id. The latest stock prices are retrieved and the order is changed to a 'sold' status. The user is redirected to a summary of their sell transaction along with status code 200.

##### HTTP PATCH:
Allows the user to modify the order such as changing quantites of stocks or if the user is a broker, changing the unit price of the stocks contained in that order. A JSON response of the newly updated order is returned along with status 201. Otherwise, if the user does not have the right authentication, an error message is returned with status code 401.

Input:
    
    {
        *"order_id": Integer
        *"user_id": Integer
        unit_price: Decimal
        "quantity": Integer
    }

Output:

    {
        *"order_id": 1
        *"stock_id": 1
        unit_price: 3.99
        "quantity": 200
        
        
##### HTTP DELETE:
Performs the same function as the POST request.

##### Other HTTP Request Methods:
An error message is returned with status 405


### "profile"

##### HTTP GET:
Returns the user's profile information and renders it on the html template along with status code 200. If the user is not authenticated, an error message is returned with status code 401.

Output:

    {
        *"user_id": Integer 
        "username": String 
        *"firstname": String
        *"lastname": String 
        *"email": String
    }

##### HTTP DELETE:
Deletes the user from the platform and returns a confirmation message with status code 200.

Output: "User successfully deleted"


##### HTTP POST:
Performs the same function as the DELETE request.

##### HTTP PATCH:
Allows the user to amend their personal information which will then be updated on the profile page with status 200.
Redirects back to the profile page.
   
##### Other HTTP Request Methods:
An error message is returned with status 405


### "company/search"

##### HTTP GET:
Renders the search page to allow the user to search for company information along with status code 200.

##### HTTP POST:
Processes the user input in the form and searches for a company based on the ticker entered by the user. If the company does not exist, then an error message is returned with status code 404. Otherwise, the information is rendered on a template with status code 200.

##### Other HTTP Request Methods:
An error message is returned with status 405


## Home Views (/home)
### "/"

##### HTTP GET:
Renders the homepage along with status code 200.

##### Other HTTP Request Methods:
An error message is returned with status 405

### "about"

##### HTTP GET:
Renders the about us page along with status code 200.

##### Other HTTP Request Methods:
An error message is returned with status 405

### "contact"

##### HTTP GET:
Renders the contact us page along with status code 200.

##### Other HTTP Request Methods:
An error message is returned with status 405


## Stock Views (/stocks)

### "/"

##### HTTP GET:
Performs webscraping to randomly select companies from the list of S&P500 companies each time the page is loaded and displays the search page for the user to search for stock data along with status code 200.

##### HTTP POST
Loads the stock details page with status code 200. and creates new stock details objects and company objects if they do not already exist in the database.

##### Other HTTP Request Methods:
An error message is returned with status 405


### "search"
Performs the same function as the default stocks "/" view


### "cart"

##### HTTP POST:
Loads the current user's cart including any stocks they have previously added but not checked out with status code 200. If they are not authenticated, then an error message is returned with status code 405. 

##### Other HTTP Request Methods:
An error message is returned with status 405


### "cart/buy/<str:stock_ticker>"

##### HTTP GET:
Allows the user to add a stock into their cart specified by the stock ticker. If a database error occurs, an error message is returned with status code 400. If they are not authenticated, then an error message is returned with status code 405. 

##### Other HTTP Request Methods:
An error message is returned with status 405


### "cart/remove/<str:stock_ticker>"

##### All HTTP Request Methods:
The selected stock specified by the stock ticker is removed from the user's cart with status code 200 and the user's cart is reloaded to reflect the change.


### "buy"

##### All HTTP Request Methods:
Executes the order with all of the stock currently in the user's cart and redirects the user to the order confirmation page. If a database error occurs, an error message is returned with status code 400. If they are not authenticated, then an error message is returned with status code 405. 


### "search/industry/<str:industry>"

##### HTTP GET:
Allows the user to search for stock information by the industry the company is part of. This renders a list of different industries along with status code 200. If a database error occurs, an error message is returned with status code 400. If they are not authenticated, then an error message is returned with status code 405. 

##### Other HTTP Request Methods:
An error message is returned with status 405


## Users View (/users)
*This is a view that implements the Django Rest Framework*

### "/"

##### HTTP GET:
This returns a list of all the users currently registered on the platform as a list along with status code 200. If the user is not authenticated, then an error message is returned with status 401.

##### Other HTTP Request Methods:
An error message is returned with status 405


