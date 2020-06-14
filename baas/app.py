import json
import os
import base64
import random

from flask import Flask, request

app = Flask(__name__)

BIRB_FILE = "../birbs.json"


@app.route("/get_birb")
def get_birb():
    with open(BIRB_FILE, "r") as f:
        birbs = json.load(f)
        return random.choice(birbs.get("birbs"))

@app.route("/get_birb_image/<uuid>")
def get_birb_image(uuid):
    with open(os.path.join("../birbs", f"{uuid}.jpg"), "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
        print(encoded_image)
        return json.dumps({"image": encoded_image})

@app.route("/get_birbs")
def get_birbs():
    with open("../birbs.json", "r") as f:
        return json.load(f)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
