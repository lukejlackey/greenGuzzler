import requests

class Quote:
    
    URL = 'https://api.quotable.io/random'
    
    def __init__(self):
        r = requests.get(self.URL)
        quote = r.json()
        self.content = quote['content']
        self.author = quote['author']


