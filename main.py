from flask import Flask, request, jsonify, send_file
import face_recognition
import numpy as np
from flask_cors import CORS
from PIL import Image, ImageDraw
import io
from json import loads
import psycopg2 as ps
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

app = Flask(__name__)
CORS(app)

conn = ps.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)

cur = conn.cursor()

@app.route('/signup', methods=['POST'])
def signUp():
    print(request.files)
    if 'img' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['img']
    
    informacion = loads(request.form["values"])

    name = informacion.get("name")
    idNumber = informacion.get("idNumber")
    speciality = informacion.get("speciality")

    if file:
        image = face_recognition.load_image_file(file)
        face_locations = face_recognition.face_locations(image)

        if face_locations:
            face_location = face_locations[0]  # Solo consideramos la primera cara encontrada
            img_encodings = face_recognition.face_encodings(image, known_face_locations=[face_location])[0]
            img_encodings_list = img_encodings.tolist()  # Convertir a lista de Python

            query = """INSERT INTO public."Usuarios" ("idNumber", face_data, name, speciality) VALUES (%s, %s, %s, %s)"""
            cur.execute(query, (idNumber, img_encodings_list, name, speciality))
            conn.commit()

            pil_image = Image.fromarray(image)
            draw = ImageDraw.Draw(pil_image)
            for (top, right, bottom, left) in face_locations:
                draw.rectangle([left, top, right, bottom], outline="green")
            byte_io = io.BytesIO()
            pil_image.save(byte_io, 'PNG')
            byte_io.seek(0)
            return send_file(byte_io, mimetype='image/png', as_attachment=True, download_name="result.png")
        else:
            return jsonify({"message": "No se encontraron caras en la imagen"}), 404
    else:
        return jsonify({"error": "Archivo no válido"}), 400


@app.route('/login', methods=['POST'])
def login():
    if 'img' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['img']

    if file:
        image = face_recognition.load_image_file(file)
        face_locations = face_recognition.face_locations(image)

        if face_locations:
            face_location = face_locations[0]  # Solo consideramos la primera cara encontrada
            unknown_encodings = face_recognition.face_encodings(image, known_face_locations=[face_location])

            if unknown_encodings:
                query_fd = """select * from public."Usuarios" """
                cur.execute(query_fd)
                known_encodings = []
                tablaUsuario = cur.fetchall()
                usuarios = []

                for (idNumber, face_data, name, speciality) in tablaUsuario:
                    usuarios.append((idNumber, name, speciality))
                    known_encodings.append(face_data)


                print(known_encodings)
                print(type(known_encodings))

                results = face_recognition.compare_faces(known_encodings, unknown_encodings[0])

                try:
                    result_index = results.index(True)
                except ValueError:
                    result_index = -1


                if result_index !=-1:
                    pil_image = Image.fromarray(image)
                    draw = ImageDraw.Draw(pil_image)
                    for (top, right, bottom, left) in face_locations:
                        draw.rectangle([left, top, right, bottom], outline="green")
                    byte_io = io.BytesIO()
                    pil_image.save(byte_io, 'PNG')
                    byte_io.seek(0)
                    idNumber, name, speciality = usuarios[result_index]

                    return jsonify({"idNumber": idNumber, "name":name, "speciality":speciality}), 200
                else:
                    return jsonify({"message": "No identificado"}), 404
            else:
                return jsonify({"message": "No se encontraron codificaciones faciales en la imagen"}), 404
        else:
            return jsonify({"message": "No se encontraron caras en la imagen"}), 404
    else:
        return jsonify({"error": "Archivo no válido"}), 400

if __name__ == '__main__':
    app.run(debug=True)
