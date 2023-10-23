from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class book(db.Model):#creamos la tabla de usuarios
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String, nullable=False, unique = True)# nos permite que el valor sa unico para poder tratarlo com una llave primaria
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    year = db.Column(db.String, nullable=False)


class users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)#hasta  aqui la tabla de usuarios


class review(db.Model):
    __tablename__="review"
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    isbn = db.Column(db.String, db.ForeignKey('books.isbn'),nullable=False)
    score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String)


    


