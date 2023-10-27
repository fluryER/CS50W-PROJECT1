import os
from flask import Flask, render_template, request, flash, redirect, url_for,session,jsonify
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_session import Session
import requests
from functools import wraps


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


load_dotenv()#Se manda a llamar las variables de entorno de .env
from werkzeug.security import generate_password_hash, check_password_hash 
app = Flask(__name__) #Se crea la app
app.config['SECRET_KEY'] = 'mysecretkey'

#Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

#Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#Set up database
engine = create_engine(os.getenv("DATABASE_URL"), pool_size=20, max_overflow=30)
db = scoped_session(sessionmaker(bind=engine))

@app.route('/') #Ruta principal del servidor
def index():
    if session.get("user_id") is None:
        return render_template('login.html')
    else:
        return render_template("busqueda.html")

@app.route('/register', methods=['GET', 'POST']) #Ruta principal del servidor
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        rname = request.form.get("name")
        remail = request.form.get("email")
        rcontraseña = request.form.get("password") 

        contraseñahash = generate_password_hash(rcontraseña)

        if not rname or not remail or not rcontraseña:
            flash('All fields are required!','danger')
            return render_template('register.html')
        try:
            verificarusuario = text("SELECT EXISTS(SELECT 1 FROM users WHERE username =:rname)")
            verificaremail = text("SELECT EXISTS(SELECT 1 FROM users WHERE  email=:remail)")

            resultado1 = db.execute(verificarusuario,{'rname':rname})
            resultado2 = db.execute(verificaremail,{'remail':remail})

            usuarioexist = resultado1.fetchone()[0]
            emailexist= resultado2.fetchone()[0]
            if usuarioexist or emailexist:
                flash('User already exists!','warning')
                return render_template('register.html')
            
            agregarusuario = text('INSERT INTO users (username,email,password) VALUES(:rname, :remail, :contraseñahash)')
            db.execute(agregarusuario, {'rname':rname, 'remail':remail,'contraseñahash':contraseñahash})
            db.commit()
            print(agregarusuario)
            db.close()
            flash('Registration successful! Please log in now!','success')

            return redirect('/')
    
        except Exception as e:
            db.rollback()
            print(e)
            return render_template('login.html')
        
@app.route('/login', methods=['POST']) #cap las cariables del diccionario
def login():

    email = request.form.get("email")
    contraseña = request.form.get("password")
    if not email or not contraseña:
        return redirect(url_for(""))#Renderiza a la ruta principal
    
    try:

        datos = text("SELECT*FROM users WHERE email=:email")
        resultado = db.execute(datos,{'email':email})
        user = resultado.fetchone()
        db.commit()
        db.close()

        if user and check_password_hash(user[3], contraseña):
            session["user_id"] = user[0]
            return render_template('busqueda.html') 
        else: 
            error = "Contraseña incorrecta, parámetros no aceptados" 
            return render_template('login.html',error=error) 
    except Exception as e:
        db.rollback()
        print(str(e))

@app.route('/logout', methods=['POST']) #
@login_required
def logout():
    session.clear()
    return redirect("/")
    

         


@app.route('/busqueda', methods=['POST'])
@login_required
def busqueda():
    busqueda = request.form.get("query")
    busqueda = busqueda.title()
    if not busqueda:
        flash("Por favor ingrese un dato a buscar", "info")
        return redirect("/")
    libros_query= text("SELECT * FROM books WHERE LOWER(isbn) LIKE LOWER(:busqueda) OR LOWER(title) LIKE LOWER(:busqueda) OR LOWER(author) LIKE LOWER(:busqueda) OR year LIKE :busqueda")
    libros = db.execute(libros_query, {"busqueda": f"%{busqueda.lower()}%"}).fetchall()
    print(libros)
    return render_template("resultados.html", books=libros)

    
@app.route('/libro_detalles/<string:isbn>', methods=['POST'])
@login_required
def libro_detalles(isbn):
    api_url = f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}'
    api_respuesta = requests.get(api_url)
    if api_respuesta.status_code == 200:
        book_info = api_respuesta.json()["items"][0]["volumeInfo"]
        description = book_info.get("description", "Descripción no disponible.")
        img = book_info.get("imageLinks", {}).get("thumbnail", "https://placehold.co/128x192?text=Image+Not+Found")
        title = book_info.get("title", "Título no disponible.")
        author = book_info.get("authors", ["Autor no disponible."])[0]
        year = book_info.get("publishedDate", "Año de publicación no disponible.")
        rating = book_info.get("averageRating", 0)
        rating_count = book_info.get("ratingsCount", 0)
        comentario = text("SELECT *FROM review WHERE isbn=:isbn")
        # return(f'{book_img}')
        comment = db.execute(comentario,{"isbn":isbn}).fetchall()
        return render_template("detalles.html", 
                               isbn=isbn,
                               description=description,
                               img=img,
                               title=title,
                               author=author,
                               year=year,
                               rating=rating,
                               rating_count=rating_count,
                               comments=comment
                        
                               )
    
    else:
        print("El api en estos momentos no esta disponible")

@app.route('/reseña', methods=['POST'])
def reseña():
     user_id = session['user_id']
     isbn = request.form.get('isbn')    
     ranting = request.form.get("puntuacion")
     comentario = request.form.get("comentario")
     review_query = text("SELECT* FROM review WHERE user_id=:user_id and isbn=:isbn")
     review = db.execute(review_query,{"user_id" :user_id, "isbn" :isbn}).fetchone()

     if review:
         return(f"Ya has enviado una reseña para este libro: {isbn}")
     
 
     if not isbn or not ranting or not comentario:
         return ("No se ha podido crear la reseña, porfavor escribe una reseña nuevamente")

     try:
         
         crear_review = text("INSERT INTO review(user_id, isbn, score, comment) VALUES(:user_id, :isbn, :ranting,:comentario)")
         db.execute(crear_review,{"user_id":user_id, "isbn" :isbn, "ranting":ranting, "comentario":comentario})
         db.commit()
         db.close()
         return redirect(f'/libro_detalles/{isbn}')
     
     except Exception as e:
         db.rollback()
         raise(e)
         return(f"Error al crear comentario")
     
@app.route('/api/<string:isbn>')  

def api(isbn):
    api = text('''SELECT b.author, b.title, b.year, b.isbn, AVG(r.score) AS average_score, COUNT(r.id) AS review_count 
         FROM books AS b 
         LEFT JOIN review AS r ON b.isbn = r.isbn 
         WHERE b.isbn = :isbn 
         GROUP BY b.author, b.title, b.year, b.isbn''')
    
    resultado_api = db.execute(api, {"isbn":isbn}).fetchone()

    if resultado_api is not None:
        author = resultado_api[0]
        title =  resultado_api[1]
        year =  resultado_api[2]
        isbn =  resultado_api[3]
        review_count = resultado_api[4]

        if resultado_api[4] is not None:
            average_score = round(resultado_api[4], 2)

        else:

            average_score = None

        resultado= {"title":title,
                        
                        "author":author,
                        "year":year,
                        "isbn": isbn,
                        "review_count":review_count,
                        "average_score":average_score }
        
        return jsonify(resultado)
    else:
        respuesta = {
            "mensaje":f"El isbn:{isbn} no se encuentra en la base de datos"

        }
        return jsonify(respuesta)

        

    

if __name__ == "__main__":
    app.run(debug=True) #Hasta aqui ya conectamos las variables de entorno

    
