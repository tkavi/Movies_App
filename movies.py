import os

from flask import Flask,request,jsonify,render_template
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api,Resource
from http import HTTPStatus
from flask_migrate import Migrate

class Config():
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://root:1234@localhost/moviesdb'

class Development_Config(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://root:1234@localhost/moviesdb'

class Production_Config(Config):
    uri = os.environ.get('DATABASE_URL')
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://","postgresql://",1)
    SQLALCHEMY_DATABASE_URI = uri

env = os.environ.get("ENV","Development")

if env == "Production":
    config_str = Production_Config
else:
    config_str = Development_Config

app = Flask(__name__)
app.config.from_object(config_str)
api = Api(app)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:welcome$1234@localhost/MovieDatabase'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://root:1234@localhost/moviesdb'
db = SQLAlchemy(app)
migrate = Migrate(app,db)

class Movie(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    title = db.Column(db.String(80), nullable = False)
    year = db.Column(db.Integer, nullable = False)
    genre = db.Column(db.String(80), nullable=False)

    @staticmethod
    def add_movie(title,year,genre):
        new_movie = Movie(title=title,year=year,genre=genre)
        db.session.add(new_movie)
        db.session.commit()
        return new_movie

    @staticmethod
    def get_movie():
        data = Movie.query.all()
        return data

    @staticmethod
    def get_movieId(id):
        data = Movie.query.filter_by(id=id).first()
        return data

    @staticmethod
    def update_movie(id):
        data = request.get_json()
        movie_id = Movie.query.filter_by(id=id).update(data)
        db.session.commit()
        return data

    @staticmethod
    def count_movies():
        count = Movie.query.count()
        return count

    @staticmethod
    def delete_movie(id):
        Movie.query.filter_by(id=id).delete()
        db.session.commit()

class AllMovies(Resource):
    def get(self):
        data = Movie.get_movie()
        movies=[]
        if data:
            for i in data:
                dict={'title':i.title,'year':i.year,'genre':i.genre}
                movies.append(dict)
            return jsonify(movies)
        else:
            return jsonify({"message":"No Data in DB",'status':HTTPStatus.OK})

    def post(self):
        data = request.get_json()
        if data:
            Movie.add_movie(title=data["title"],year=data["year"],genre=data["genre"])
            return jsonify(data,{'status':HTTPStatus.OK})

class OneMovie(Resource):
    def get(self,id):
        data= Movie.get_movieId(id)
        movie={}
        if data:
            movie['title'] = data.title
            movie['year'] = data.year
            movie['genre'] = data.genre
            return jsonify(movie,{"status":HTTPStatus.OK})
        else:
            return jsonify({"message":"Not found in Movie Database"})

    def delete(self,id):
        data = Movie.get_movieId(id)
        if data:
            Movie.delete_movie(id)
            return HTTPStatus.OK
        else:
            return HTTPStatus.NOT_FOUND

    def put(self,id):
        data = Movie.get_movieId(id)
        if data:
            movie = Movie.update_movie(id)
            return jsonify(movie,{"message":"Updated Successfully","Status":HTTPStatus.OK})
        else:
            return HTTPStatus.NOT_FOUND

api.add_resource(AllMovies,"/movies")
api.add_resource(OneMovie,"/movies/<int:id>")

@app.route("/",methods=['GET'])
def home_page():
    return render_template("home.html")

if __name__=='__main__':
    app.run()
