# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# type: ignore[1]
"""Flask Web Server"""

import os

from tempfile import TemporaryDirectory
from typing import List, Tuple

from flask import Flask, after_this_request, render_template, request
from werkzeug.exceptions import HTTPException

from docai_utils import docai_pipeline
from gcs_utils import save_document_as_csv

app = Flask(__name__)

UPLOAD_FOLDER = "/tmp"
ALLOWED_MIMETYPES = set(["application/pdf", "image/tiff", "image/jpeg"])


@app.route("/", methods=["GET"])
def index() -> str:
    """
    Web Server, Homepage
    """

    return render_template("index.html")


@app.route("/file_upload", methods=["POST"])
def file_upload() -> str:
    """
    Handle file upload request
    """
    # pylint: disable=consider-using-with
    temp_dir = TemporaryDirectory()

    @after_this_request
    def cleanup(response):
        temp_dir.cleanup()
        return response

    # Check if POST Request includes Files
    if not request.files:
        return render_template("index.html", message_error="No files provided")

    files = request.files.getlist("files")

    uploaded_filenames = save_files_to_temp_directory(files, temp_dir)

    if not uploaded_filenames:
        return render_template("index.html", message_error="No valid files provided")

    document_entities = docai_pipeline(uploaded_filenames)

    url = save_document_as_csv(document_entities)

    return render_template(
        "index.html",
        output_file_url=url,
        tables=[document_entities.to_html(classes="data", header="true", index=False)],
    )


def save_files_to_temp_directory(files, temp_dir) -> List[Tuple[str, str]]:
    """
    Save files to temporary directory
    Returns a list of tuples containing file paths and mimetypes
    """
    uploaded_filenames = []
    for file in files:

        if not file or file.filename == "":
            print("Skipping corrupt file")
            continue

        if file.mimetype not in ALLOWED_MIMETYPES:
            print(f"Invalid File Type: {file.filename}: {file.mimetype}")
            continue

        input_file_path = os.path.join(temp_dir.name, file.filename)
        file.save(input_file_path)
        uploaded_filenames.append((input_file_path, file.mimetype))
        print(f"Uploaded file: {input_file_path}, {file.mimetype}")

    return uploaded_filenames


@app.errorhandler(Exception)
def handle_exception(ex):
    """
    Handle Application Exceptions
    """
    # Pass through HTTP errors
    if isinstance(ex, HTTPException):
        return ex

    # Non-HTTP exceptions only
    return render_template(
        "index.html",
        message_error=str(ex),
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
