from flask import Flask, render_template
from dotenv import load_dotenv
load_dotenv()#se manda a llamar las variables de entorno de .env
app = Flask(__name__) #Se crea la app

@app.route('/') #Ruta principal del servidor
def login():
    return render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True) # hasta aqui ya conectamos las variables de entorno
