# Green Guzzler

Green Guzzler is a Flask app for cost conscious beer lovers to share their favorite beers. Users may upload their own breweries/beers or explore breweries/beers posted by others. Users can also rate beers based on their taste, cost, and value (i.e. was the beer worth the cost?).

# Live Version

[Green Guzzler](https://greenguzzler.link/)

This app was deployed serverlessly on the EDGE as an AWS Lambda function using Serverless Framework.

# Stack Used

This app follows a standard MVC design pattern. For the backend, I chose the Flask microframework for its flexibility and compatipility with Serverless Framework. Jinja2 templates were used to render all frontend views. I chose a MySQL relational database hosted on AWS RDS to store the project's persistent data.

# Screenshots

Home Screen

![alt text](https://github.com/lukejlackey/greenGuzzler/blob/master/readmeImages/home.png?raw=true)

Breweries

![alt text](https://github.com/lukejlackey/greenGuzzler/blob/master/readmeImages/breweries.png?raw=true)

Create Brewery

![alt text](https://github.com/lukejlackey/greenGuzzler/blob/master/readmeImages/create.png?raw=true)

View Beer

![alt text](https://github.com/lukejlackey/greenGuzzler/blob/master/readmeImages/beer.png?raw=true)

View Brewery

![alt text](https://github.com/lukejlackey/greenGuzzler/blob/master/readmeImages/brewery.png?raw=true)

User Dashboard

![alt text](https://github.com/lukejlackey/greenGuzzler/blob/master/readmeImages/dash.png?raw=true)

Login/Register

![alt text](https://github.com/lukejlackey/greenGuzzler/blob/master/readmeImages/login.png?raw=true)