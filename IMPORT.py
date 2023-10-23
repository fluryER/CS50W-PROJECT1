import csv
import os 
from dotenv import load_dotenv
load_dotenv()
from sqlalchemy import create_engine, text #create_engine crea un motor de base de datos y text sirve para crear consultas de sql de manera textual
from sqlalchemy.orm import sessionmaker,scoped_session # sessionmaker crea una consulta cuando nos conectemos a la base de datos y scoped_ssion sirve para establecer sesiones definidas por el usuario


engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))# tenemos el motor y la sesion que la mandamos al mismo


def main():

    f = open("boks.csv")
    reader = csv.reader(f)
    next(reader)# omite la cabecera del archivo
    for isbn, title, author, year in reader:

        try:
            consulta = text("INSERT INTO books (isbn, title, author, year) VALUES (:isbn,:title, :author, :year)" )
            db.execute(consulta, {"isbn": isbn, "title" : title, "author": author, "year": year})
            print('Se ha insertado correctamente')
            print (consulta)

        except Exception as e:
            print ("Ocurrio un error",e)
            db.rollback()


    db.commit() #confirma los cambios en la base de datos

if __name__ == "__main__":
    main()      




