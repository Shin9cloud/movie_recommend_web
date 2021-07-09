from flask import Flask, request, render_template
from datetime import date
import json
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

import pandas as pd
import requests
from fetch import movie, movie_collection
from ml import RECOMMEND


# flask 기본 문법 (반드시쓴다)
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST']) ## 라우팅 방식은 겟, 포스트
def index():
    
    if request.method == "GET":
        year = date.today().year
        id_year = f'http://api.themoviedb.org/3/discover/movie?api_key=da396cb4a1c47c5b912fda20fd3a3336&primary_release_year={year}&sort_by=popularity.desc'
        # data = requests.get(id_year)
        # print(data)
        # return data

        # top_year = json.loads(requests.get(id_year).text)
        
        # top_year.results = []
        # top_year.fetch(id_year)
        
        # print(top_year.results)
        # return top_year.results
        # print(results)
        top_year = movie_collection()
        top_year.results =[]
        top_year.fetch(id_year)
        genres = json.loads(requests.get("https://api.themoviedb.org/3/genre/movie/list?api_key=da396cb4a1c47c5b912fda20fd3a3336&language=en-US").text)
        
        top_genre_collection =[]
        for genre in genres['genres']:
            # print(genre['id'])
            genre_id = 'https://api.themoviedb.org/3/discover/movie?api_key=da396cb4a1c47c5b912fda20fd3a3336&with_genres={}&sort_by=popularity.desc'.format(genre["id"])
            top_genre = movie_collection()
            top_genre.results =[]
            top_genre.fetch(genre_id)
            top_genre_id = [top_genre.results, genre["name"]]
            top_genre_collection.append(top_genre_id)

        return render_template("home.html", top_year= top_year.results, year= year, top_genre= top_genre_collection)

    elif request.method =='POST':

        # print(request.form['query'])
        key_word = request.form['query']
        id_url = f"http://api.themoviedb.org/3/search/movie?api_key=da396cb4a1c47c5b912fda20fd3a3336&query={key_word}"
        movie_dic = movie_collection()
        movie_dic.results =[]
        movie_dic.fetch(id_url)
        # print(movie_dic.results)

        return render_template("landing.html", movie = movie_dic.results, key_word= key_word)

@app.route('/details/<id>', methods=['GET', 'POST'])

def details(id):
    url = f"http://api.themoviedb.org/3/movie/{id}?api_key=da396cb4a1c47c5b912fda20fd3a3336"
    data = json.loads(requests.get(url).text)
    data_json = movie(data["id"],data["title"],data["poster_path"],data["vote_average"],data["release_date"],data["overview"])
    # print(data_json)
    return render_template("details.html", movie = data_json)

@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    df2 = pd.read_csv('./model/tmdb.csv', encoding='utf-8')
    df2 = df2.reset_index()
    all_titles = [df2['title'][i] for i in range(len(df2['title']))]
    
    if request.method == 'GET':
        return render_template('recommend.html')
    elif request.method == 'POST':
        
        print(len(all_titles))
        m_name = request.form['movie_name']
        # print(m_name.title())
        m_name = m_name.title()
        if m_name not in all_titles:
            return render_template('negative.html', name= m_name)
        else:
            # result_final = RECOMMEND(TfidfVectorizer).get_recommendation(m_name)
            recommend = RECOMMEND(TfidfVectorizer)
            result_final = recommend.get_recommendation(m_name)
            # print(result_final)

            # result_final = get_recommendation(m_name)
            # print(type(result_final))

            data = []
            for i in range(len(result_final)):
                data.append((result_final.iloc[i][0], result_final.iloc[i][1]))
            return render_template('positive.html', movie_data = data, search_name = m_name)
    

    # return "page"

if __name__ == "__main__":
    app.run(port= 5000, debug=True) ## localhost:5000 / 오류메시지 웹창에 보이게 하는거 debug=True (실제 개발할때는 비공개)