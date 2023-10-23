import os #mando a llamar las variables de entorno
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import *
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)#creamos la instancia de la app de flask
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

def main():

    db.create_all()


if __name__ == "__main__":#ejecutamos la funcion main en el codigo mientras ete dentro del script del mismo archivo
    with app.app_context():
        main()
        
    

