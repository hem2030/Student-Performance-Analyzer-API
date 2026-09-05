from fastapi import FastAPI,HTTPException,Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt,JWTError
from datetime import datetime,timedelta
from Models import SECRET_KEY,ALGORITHM
from Database import get_db

app = FastAPI()

oauth2_Scheme=OAuth2PasswordBearer(tokenUrl="login")

pwd_Context=CryptContext(
    schemes = ["bcrypt"],
    deprecated = "auto"
)

get_db()

class LoginData(BaseModel):
    name:str
    attendance:float
    maths:float
    python:float
    cgpa:float

def create_token(name):
    expire = datetime.utcnow()+timedelta(minutes=20)

    data = {
        "Name" : name,
        "exp" : expire
    }

    token=jwt.encode(
        data,
        SECRET_KEY,
        algorithm = ALGORITHM
    )

    return token

@app.post("/login")
def login(data: LoginData):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
         CREATE TABLE IF NOT EXISTS fast(
         id INT AUTO_INCREMENT PRIMARY KEY,
         name VARCHAR(100) NOT NULL,
         attendance FLOAT NOT NULL,
         maths FLOAT NOT NULL,
         python FLOAT NOT NULL,
         cgpa FLOAT NOT NULL)""")
    

    cursor.execute("""
         INSERT INTO fast(name,attendance,maths,python,cgpa) VALUES(%s,%s,%s,%s,%s)""",
         (data.name,data.attendance,data.maths,data.python,data.cgpa))

    db.commit()

    student_id = cursor.lastrowid

    return{
        "Message" : "Student Added Sucessfully",
        "student_id" : student_id
    }

@app.get("/all")
def get_students():
    db = get_db()

    cursor = db.cursor()

    cursor.execute("SELECT * FROM fast")

    fast = cursor.fetchall()

    return{
        "Student" : fast
    }

# specific student mate no output-----


@app.get("/all/{student_id}")
def get_one(student_id : int):

    db = get_db()
    cursor = db.cursor()
   
    cursor.execute(
        "SELECT id,name,attendance,maths,python,cgpa FROM fast WHERE id = %s",
        (student_id,)
    )

    row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            STATUS_CODE = 404,
            detail = "Student Not Found"
        )
    return{
        "Student_id" : row[0],
        "Name" : row[1],
        "Attendance" : row[2],
        "Maths"  : row[3],
        "Python" : row[4],
        "CGPA" : row[5]
    }

@app.get("/analysis")
def analysis():

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
         SELECT attendance,maths,python,cgpa FROM fast """)

    data = cursor.fetchall()

    total_student = len(data)

    average_attendance = sum(row[0] for row in data)/total_student

    average_maths = sum(row[1] for row in data)/total_student

    average_python = sum(row[2] for row in data)/total_student

    average_cgpa = sum(row[3] for row in data)/total_student

    return{
        "total_students" : total_student,
        "average_attendance" : average_attendance,
        "average_maths" : average_maths,
        "average_python" : average_python,
        "average_cgpa" : average_cgpa
    }
