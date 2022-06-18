from flask import Flask, request
from movies import models
from movies import client

app = Flask(__name__)
models.start_mappers()

@app.route("/hello", methods=["GET"])
def hello_world():
    return """<form>
                <label for="fname">Full name:</label><br>
                <input type="text" id="fname" name="fname"><br>

                <br><h2><label for="genreOne">Choose your favorite movie genres down below (will only consider the first 3 selected):</label></h2>

                <input type="checkbox" id="genreOne" name="genreOne" value="genreOne">
                <label for="genreOne">1. Comedy</label><br>

                <input type="checkbox" id="genreTwo" name="genreTwo" value="genreTwo">
                <label for="genreTwo">2. Drama</label><br>

                <input type="checkbox" id="genreThree" name="genreThree" value="genreThree">
                <label for="genreThree">3. Sci-Fi</label><br>

                <input type="checkbox" id="genreFour" name="genreFour" value="genreFour">
                <label for="genreFour">4. Romantic</label><br>

                <input type="checkbox" id="genreFive" name="genreFive" value="genreFive">
                <label for="genreFive">5. Adventure</label><br>

                <br><h3><label for="genreOne">Rating (Enable = descending order, Disable = ascending order):</label></h3>

                <input type="radio" id="ratingEnable" name="ratingEnable" value="ratingEnable">
                <label for="ratingEnable">Enable</label><br>
                <input type="radio" id="ratingDisable" name="ratingDisable" value="ratingDisable">
                <label for="ratingDisable">Disable</label><br>

                <br><input type="submit" value="Submit">
                <button> <a href="/register">Submit</a></button>
            </form>""", 200

@app.route("/register", methods=["GET"])
def start():
    return """<table>
                <tr>
                    <th> user.name </th> 
                    <th> list.content </th> 
                    <th> / </th> 
                    <th> / </th> 
                    <th> / </th> 
                    <th> / </th> 
                </tr>""", 200