from flask import Flask, render_template, request, send_from_directory, render_template_string, jsonify
import os
import subprocess
import re

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'

def process_uploaded_file(file):
    # Create 'uploads' directory if it doesn't exist
    os.makedirs('uploads', exist_ok=True)

    # Process the uploaded file
    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)
    return file_path


@app.route("/", methods=['GET', 'POST'])
def tester():
    if request.method == 'POST':
        # Check if the 'file' key is in the request.files dictionary
        if 'file' in request.files:
            uploaded_file = request.files['file']
            if uploaded_file.filename != '':
                # Process the uploaded file
                file_path = process_uploaded_file(uploaded_file)

                # Now you can use file_path in your detection logic
                # For example, you can pass it as an argument to your detection script
                command = f"python yolov7/detect.py --weights yolov7/waste.pt --conf 0.4 --img-size 640 --source {file_path}"
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
                    # Return the final_result as JSON
                    return jsonify({"result": final_result})
                except subprocess.CalledProcessError as e:
                    print(e.output)
                    return render_template('errors.html', error=e.output), 500
            else:
                return render_template('errors.html', error="Uploaded file has no filename"), 400
        else:
            return render_template('errors.html', error="No 'file' in request.files"), 400
    else:
        return render_template('errors.html', error="Invalid request method"), 405

if __name__ == "__main__":
    app.run(debug=True)