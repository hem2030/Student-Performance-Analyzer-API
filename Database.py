import pymysql
def get_db():
    db = pymysql.connect(

        host="localhost",

        user="root",

        password="kalyaniraj",

        database="om_db"
    )
    return db
