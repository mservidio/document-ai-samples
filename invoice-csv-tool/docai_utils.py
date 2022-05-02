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

"""Document AI Utility Functions"""

from os.path import basename as path_basename
from typing import List, Tuple, Dict

import pandas as pd

from google.api_core.exceptions import GoogleAPICallError
from google.api_core.client_options import ClientOptions
from google.cloud import documentai_v1 as documentai

from consts import (
    DEFAULT_MIME_TYPE,
    DOCAI_PROCESSOR_ID,
    DOCAI_PROCESSOR_LOCATION,
    DOCAI_PROJECT_ID,
)

# Instantiates a client
documentai_client = documentai.DocumentProcessorServiceClient(
    client_options=ClientOptions(
        api_endpoint=f"{DOCAI_PROCESSOR_LOCATION}-documentai.googleapis.com"
    )
)


def process_document_bytes(
    file_content: bytes,
    mime_type: str = DEFAULT_MIME_TYPE,
    project_id: str = DOCAI_PROJECT_ID,
    location: str = DOCAI_PROCESSOR_LOCATION,
    processor_id: str = DOCAI_PROCESSOR_ID,
) -> documentai.Document:
    """
    Processes a document using the Document AI API.
    Takes in bytes from file reading, instead of a file path
    """

    # The full resource name of the processor, e.g.:
    # projects/project-id/locations/location/processor/processor-id
    # You must create new processors in the Cloud Console first
    resource_name = documentai_client.processor_path(project_id, location, processor_id)

    # Use the Document AI client to process the sample form
    result = documentai_client.process_document(
        request=documentai.ProcessRequest(
            name=resource_name,
            raw_document=documentai.RawDocument(
                content=file_content, mime_type=mime_type
            ),
        )
    )

    return result.document


def extract_document_entities(document: documentai.Document) -> dict:
    """
    Get all entities from a document and output as a dictionary
    Format: entity.type_: entity.mention_text OR entity.normalized_value.text
    """
    document_entities = {}
    for entity in document.entities:
        # Use EKG Enriched Data if available
        normalized_value = getattr(entity, "normalized_value", None)
        value = normalized_value.text if normalized_value else entity.mention_text

        document_entities[entity.type_] = value

    return document_entities


def docai_pipeline(local_files: List[Tuple[str, str]]) -> pd.DataFrame:
    """
    Process Documents
    """

    all_documents: List[Dict] = []
    for file_path, mime_type in local_files:
        file_name = path_basename(file_path)
        # Read File into Memory
        with open(file_path, "rb") as file:
            file_content = file.read()

            # Run Parser
            try:
                document_proto = process_document_bytes(file_content, mime_type)
            except GoogleAPICallError:
                print("Skipping file:", file_path)
                continue

            # Extract Entities from Document
            document_entities = extract_document_entities(document_proto)

            document_entities["source_file"] = file_name
            all_documents.append(document_entities)

    return pd.DataFrame(all_documents)
