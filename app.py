# Importing the Libraries

from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import pymongo

app = Flask(__name__)

@app.route('/', methods=['POST','GET'])
def index():
    if request.method == 'POST':
        searchString = request.form['content'].replace(" ","")
        try:
            dbConn = pymongo.MongoClient("mongodb://localhost:27017/")
            db = dbConn['WebCrawler']
            reviews = db[searchString].find({})
            if reviews.count() > 0:
                return render_template('results.html', reviews = reviews)
            else:
                url = "https://www.flipkart.com/search?q=" + searchString
                uClient = urlopen(url)
                flip_page = uClient.read()
                uClient.close()
                flipkart_html = bs(flip_page, "html.parser")
                boxes = flipkart_html.findAll('div', {'class': 'bhgxx2 col-12-12'})
                del boxes[0:3]
                box = boxes[0]
                productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
                productResult = requests.get(productLink)
                prodHtml = bs(productResult.text, "html.parser")
                commentBoxes = prodHtml.find_all('div', {'class': "_3nrCtb"})

                table = db[searchString]

                reviews = []

                for comment in commentBoxes:
                    try:
                        name = comment.div.div.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text
                    except:
                        name = 'Anonymous'

                    try:
                        rating = comment.div.div.div.div.text
                    except:
                        rating = 'No Rating'

                    try:
                        commentHead = comment.div.div.div.p.text
                    except:
                        commentHead = 'No Comment Heading'

                    try:
                        comTag = comment.div.div.find_all('div', {'class': ''})
                        customerComment = comTag[0].div.text
                    except:
                        customerComment = 'No comment given by the customer'

                    my_dict = {'Product': searchString, "Name": name, "Rating": rating,
                               "Comment Heading": commentHead, "Comment": customerComment}
                    x = table.insert_one(my_dict)
                    reviews.append(my_dict)

                return render_template('results.html', reviews = reviews)
        except:
            return "Error Occured!!"

    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(port=8000, debug=True)