from flask import Flask, request, jsonify, send_file
import face_recognition
import numpy as np
from PIL import Image, ImageDraw
import io

app = Flask(__name__)

known_encodings = [np.random.rand(128)]


@app.route('/signup', methods=['POST'])
def signUp():
    global known_encodings
    if 'img' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['img']

    if file:
        image = face_recognition.load_image_file(file)
        face_locations = face_recognition.face_locations(image)

        if face_locations:
            face_location = face_locations[0]  # Solo consideramos la primera cara encontrada
            img_encodings = face_recognition.face_encodings(image, known_face_locations=[face_location])
            print(f"Encodings a guardar:", img_encodings)
            known_encodings.append(img_encodings[0])
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
    global known_encodings  # Reemplazar por la BD
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
                results = face_recognition.compare_faces(known_encodings, unknown_encodings[0])
                if True in results:
                    pil_image = Image.fromarray(image)
                    draw = ImageDraw.Draw(pil_image)
                    for (top, right, bottom, left) in face_locations:
                        draw.rectangle([left, top, right, bottom], outline="green")
                    byte_io = io.BytesIO()
                    pil_image.save(byte_io, 'PNG')
                    byte_io.seek(0)
                    return jsonify({"message": "devolver informacion del usuario identificado"}), 200
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
