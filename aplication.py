import os
from flask import Flask, render_template, request, flash, redirect, url_for,session
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_session import Session
from helpers import login_required



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




    return render_template('login.html')

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
    

         




    



if __name__ == "__main__":
    app.run(debug=True) #Hasta aqui ya conectamos las variables de entorno
