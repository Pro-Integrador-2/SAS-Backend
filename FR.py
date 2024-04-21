from flask import Flask, request, jsonify, send_file
import face_recognition
import numpy as np
from PIL import Image, ImageDraw
import io

app = Flask(__name__)

# Encodings conocidos, deberia almacenarse en una BD
known_encodings = [np.random.rand(128)]

@app.route('/login', methods=['POST'])
def login():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['img']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        face_locations = face_recognition.face_locations(file)[0]
        image = face_recognition.load_image_file(file)
        unknown_encodings = face_recognition.face_encodings(image, known_face_locations=[face_locations])

        if unknown_encodings:
            results = face_recognition.compare_faces(known_encodings, unknown_encodings[0])
            if True in results:
                pil_image = Image.fromarray(image)
                draw = ImageDraw.Draw(pil_image)
                face_locations = face_recognition.face_locations(image)
                for (top, right, bottom, left) in face_locations:
                    draw.rectangle(((left, top), (right, bottom)), outline="green")

                byte_io = io.BytesIO()
                pil_image.save(byte_io, 'PNG')
                byte_io.seek(0)
                return send_file(byte_io, mimetype='image/png', as_attachment=True, attachment_filename='identified.png')
            else:
                return jsonify({"message": "No identificado"}), 404
        else:
            return jsonify({"message": "No faces found in the image"}), 404
    else:
        return jsonify({"error": "file not valid"}), 400


if __name__ == '__main__':
    app.run(debug=True)
