# runs perfectly on pythonanywhere
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, session , send_from_directory , send_file
import os
import subprocess
import re

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'images'

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["GET", "POST"])
def tester():
    if request.method == "POST":
        command = f"python yolov7/detect.py --weights yolov7/waste.pt --conf 0.4 --img-size 640 --source yolov7/glass206.jpg"
        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
            print(result)
            # extract the desired information
            result_phrase_match = re.search(r'model is traced!(.*?Done\.)', result, re.DOTALL)
            if result_phrase_match:
                result_phrase = result_phrase_match.group(1).replace(re.search(r'\d', result_phrase_match.group(1)).group(), "").replace(", Done.", "").strip()
                print(result_phrase)

                if (result_phrase == "glass"):
                        final_result = 0
                if (result_phrase == "metal"):
                        final_result = 1
                if (result_phrase == "plastic"):
                        final_result = 2
                if (result_phrase == "paper"):
                        final_result = 3
                if (result_phrase == "other"):
                        final_result = 4
            return render_template('result.html', result=final_result)
        except subprocess.CalledProcessError as e:
            print(e.output)
            return render_template('errors.html', error = e.output)

if __name__ == "__main__":
    app.run(debug=True)