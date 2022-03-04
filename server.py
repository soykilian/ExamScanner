from flask import Flask, request
from flask_cors import CORS
from flask_autoindex import AutoIndex
from omr.omr import get_answers

import json
import os
import threading
import requests
import sys
import shutil

import pandas as pd
import numpy as np

import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# -- DATOS DEL EXAMEN
EXAMEN = "INTRODUCCIÓN A LA INGENIERÍA DE TELECOMUNICACIÓN - EXAMEN FINAL"
EMAIL_COORDINADOR = "pruebasSDG2+coordinador@gmail.com"
N_ALTERNATIVAS = 5
RESPUESTAS_CORRECTAS = [
    ["A", "B", "C", "A", "B", "A", "C", "E", "E", "E", "C", "D"],
    ["C", "A", "B", "C", "A", "B", "A", "C", "E", "A", "B", "D"],
    ["A", "B", "C", "A", "B", "A", "C", "E", "A", "B", "C", "D"],
    ["A", "B", "A", "B", "C", "A", "C", "E", "A", "B", "C", "D"]
]

SENDER_EMAIL = sys.argv[1]
PASSWORD_EMAIL = sys.argv[2]
SMTP_DOMAIN = sys.argv[3]
SMTP_PORT = sys.argv[4]

# -- PATHS NECESARIOS PARA EL FUNCIONAMIENTO DEL PROGRAMA
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

DATA_NAME = 'data.csv'
DATA_PATH = os.path.join(CURRENT_PATH, DATA_NAME)

IMAGE_ORIG_NAME = 'imagen_original.jpg'
IMAGE_ORIG_PATH = os.path.join(CURRENT_PATH, IMAGE_ORIG_NAME)

IMAGE_READ_NAME = 'imagen_leida.jpg'
IMAGE_READ_PATH = os.path.join(CURRENT_PATH, IMAGE_READ_NAME)

IMAGE_PREVIEW_NAME = 'imagen_preview.jpg'
IMAGE_PREVIEW_PATH = os.path.join(CURRENT_PATH, IMAGE_PREVIEW_NAME)

STATIC_NAME = 'static'
STATIC_PATH = os.path.join(CURRENT_PATH, STATIC_NAME)


app = Flask(__name__,
            static_url_path='',
            static_folder='static')

CORS(app)

def get_response():
    user_DNI, user_version, user_answers = analyze_picture()
    user_answers = user_answers[:len(RESPUESTAS_CORRECTAS[0])]

    grade, num_correctas = calculate_grade(user_answers, user_version)

    beauty_user_DNI = ''.join(user_DNI)
    beauty_user_answers = ''.join(user_answers)

    surname, name, email = updateCSV(beauty_user_DNI, user_version, beauty_user_answers, grade)

    processThread = threading.Thread(target=sendMail, args=[user_version, user_answers, grade, surname, name, email])
    processThread.start()

    processThread = threading.Thread(target=save_to_folder, args=[beauty_user_DNI])
    processThread.start()

    # print(beauty_user_DNI)
    ranking = get_ranking(beauty_user_DNI)
    media = get_media()

    response = {
        "user_DNI": user_DNI,
        "user_version": user_version,
        "user_answers": user_answers,
        "grade": grade,
        "num_correctas": num_correctas,
        "ranking": ranking,
        "media": media
    }

    return response

def analyze_picture():
    DNI, version, answers, _ = get_answers(IMAGE_ORIG_PATH, IMAGE_READ_PATH)

    user_answers = []
    for i, answer in enumerate(answers):
        user_answers.append(answer)

    user_DNI = []
    for i, DNI in enumerate(DNI):
        user_DNI.append(DNI)

    return user_DNI, version, user_answers

def calculate_grade(user_answers, user_version):

    if user_version == 0:
        return "NOTA DESCONOCIDA - PÓNGASE EN CONTACTO CON EL COORDINADOR DE LA ASIGNATURA", 0

    calificacion = 0
    num_correctas = 0

    for index, value in enumerate(RESPUESTAS_CORRECTAS[user_version-1]):

        if value == user_answers[index]:
            calificacion += 1*N_ALTERNATIVAS
            num_correctas += 1
        elif (user_answers[index] != 'N/A'):
            calificacion -= 1

    calificacion_maxima = len(RESPUESTAS_CORRECTAS[0])
    grade = round((calificacion/(N_ALTERNATIVAS * calificacion_maxima*0.1)), 2)

    return grade, num_correctas


def sendMail(user_version, user_answers, grade, surname, name, email):

    #print(SENDER_EMAIL, PASSWORD_EMAIL, SMTP_DOMAIN, SMTP_PORT)

    beauty_user_answers = '\n\n'
    for index, value in enumerate(user_answers):
        beauty_user_answers += str(index+1) + ".\t\t" + "Su respuesta\t|\tRespuesta correcta:\t" + value \
        + "\t|\t" + str(RESPUESTAS_CORRECTAS[user_version-1][index]) + "\n"

    subject = "Respuestas de " + EXAMEN
    body = "Estimado " + name + ' ' + surname + ", para la versión " + str(user_version) \
        + " se han leído las respuestas " + beauty_user_answers + "\nLa nota final (sobre 10) es " \
        + str(grade) + "\nSe adjunta la imagen correspondiente"

    receiver_email = email


    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = receiver_email
    message["Subject"] = subject
    #message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    #---------------------------------------------------------------
    # Attach imagen_original
    filename = IMAGE_ORIG_PATH  # In same directory as script

    # Open image file in binary mode
    with open(filename, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)

    filename = "examen_original.jpg"
    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    #---------------------------------------------------------------

    #---------------------------------------------------------------
    # Attach imagen_modificada
    filename = IMAGE_READ_PATH  # In same directory as script

    # Open image file in binary mode
    with open(filename, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)

    filename = "examen_leido.jpg"
    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    #---------------------------------------------------------------


    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_DOMAIN, SMTP_PORT, context=context) as server:
        server.login(SENDER_EMAIL, PASSWORD_EMAIL)
        server.sendmail(SENDER_EMAIL, receiver_email, text)

    #print(receiver_email)

    #with smtplib.SMTP("smtp.mailtrap.io", 2525) as server:
    #    server.login("582897ddd2268b", "7a5fa911b7dfbc")
    #    server.sendmail("prueba@prueba.com", receiver_email, text)

    #print("OK")

def save_to_folder(DNI):
    shutil.copy(IMAGE_ORIG_NAME, 'imagenes')
    os.rename(os.path.join('imagenes', IMAGE_ORIG_NAME), os.path.join('imagenes', str(DNI) + "_imagen_orig.jpg"))

    shutil.copy(IMAGE_READ_PATH, 'imagenes')
    os.rename(os.path.join('imagenes', IMAGE_READ_NAME), os.path.join('imagenes', str(DNI) + "_imagen_leida.jpg"))


def updateCSV(user_DNI, user_version, user_answers, user_grade):
    df = pd.read_csv(DATA_PATH, sep=',')

    #df.loc[df['DNI'] == int(user_DNI), 'Version'] = user_version
    #df.loc[df['DNI'] == int(user_DNI), 'Answers'] = user_answers
    df.loc[df['DNI'] == int(user_DNI), 'Nota'] = user_grade

    if df.loc[df['DNI'] == int(user_DNI)].size != 0:
        surname = df.loc[df['DNI'] == int(user_DNI), 'Surname'].values[0]
        name = df.loc[df['DNI'] == int(user_DNI), 'Name'].values[0]
        email = df.loc[df['DNI'] == int(user_DNI), 'Email'].values[0]

        df.to_csv(DATA_PATH, header=True, sep=',', index=False)
        return surname, name, email

    else:
        return "DESCONOCIDO", "DESCONOCIDO", EMAIL_COORDINADOR

def get_media():
    df = pd.read_csv(DATA_PATH, sep=',')
    media = df['Nota'].mean()
    return round(media, 2)

def get_ranking(DNI):
    df = pd.read_csv(DATA_PATH, sep=',')
    df = df.sort_values('Nota', ascending=False)
    df = df.set_index('DNI')

    return (int)(np.where(df.index==int(DNI))[0][0] + 1)

files_index = AutoIndex(app, os.path.curdir + '/imagenes', add_url_rules=False)
# Custom indexing
@app.route('/imagenes')
@app.route('/imagenes/<path:path>')
def autoindex(path='.'):
    return files_index.render_autoindex(path)

@app.route('/get_answers', methods=['GET'])
def get_cam_picture():

    response = requests.get("http://127.0.0.1:8080?action=snapshot")
    file = open(IMAGE_ORIG_NAME, "wb")
    file.write(response.content)
    file.close()

    response = get_response()

    response_json = app.response_class(
        response=json.dumps(response),
        status=200,
        mimetype='application/json'
    )

    return response_json

@app.route('/get_answers', methods=['POST'])
def get_post_picture():

    image = request.files["image"]
    image.save(IMAGE_ORIG_PATH)

    response = get_response()

    response_json = app.response_class(
        response=json.dumps(response),
        status=200,
        mimetype='application/json'
    )

    return response_json


@app.route('/get_media', methods=['GET'])
def send_media():

    response = get_media()

    response_json = app.response_class(
        response=json.dumps(response),
        status=200,
        mimetype='application/json'
    )

    return response_json


@app.route('/get_ranking', methods=['GET'])
def send_ranking():

    DNI = request.args.get('DNI')
    response = get_ranking(DNI)

    response_json = app.response_class(
        response=json.dumps(response),
        status=200,
        mimetype='application/json'
    )

    return response_json


if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug=True)
