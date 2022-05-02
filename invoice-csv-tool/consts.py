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

"""Constant Definitions"""

import yaml


def read_yaml(file_path):
    """
    Reads a yaml file and returns a dictionary
    """
    with open(file_path, "r", encoding="utf8") as file:
        return yaml.safe_load(file)


CONFIG_FILE_PATH = "config.yaml"
CONFIG = read_yaml(CONFIG_FILE_PATH)

DOCAI_PROJECT_ID = CONFIG["docai_project_id"]
DOCAI_PROCESSOR_LOCATION = CONFIG["docai_processor_location"]
DOCAI_PROCESSOR_ID = CONFIG["docai_processor_id"]

DEFAULT_MIME_TYPE = "application/pdf"

# GCS
GCS_PROJECT_ID = DOCAI_PROJECT_ID
GCS_BUCKET = CONFIG["gcs_bucket"]
