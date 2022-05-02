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

"""Google Cloud Storage Function"""

import datetime

from pandas import DataFrame

from google.cloud import storage

from consts import GCS_BUCKET

gcs_client = storage.Client()


def save_document_as_csv(document_entities: DataFrame) -> str:
    """
    Save document entities as CSV
    """
    session_id = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    output_filename = f"{session_id}_invoice.csv"
    print(f"Saving document entities as CSV {output_filename}")

    bucket = gcs_client.get_bucket(GCS_BUCKET)
    blob = bucket.blob(output_filename)
    blob.upload_from_string(document_entities.to_csv(index=False), "text/csv")

    url = f"https://storage.googleapis.com/{GCS_BUCKET}/{output_filename}"
    return url
