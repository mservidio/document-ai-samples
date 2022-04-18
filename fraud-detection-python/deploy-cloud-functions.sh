#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

source "${DIR}/.env.local"

gcloud functions deploy process-invoices \
--region=${CLOUD_FUNCTION_LOCATION} \
--entry-point=process_invoice \
--runtime=python39 \
--service-account=${SERVICE_ACCOUNT} \
--source=cloud-functions/process-invoices \
--timeout=400 \
--env-vars-file=cloud-functions/process-invoices/.env.yaml \
--trigger-resource=${INPUT_BUCKET} \
--trigger-event=google.storage.object.finalize

gsutil iam ch serviceAccount:${SERVICE_ACCOUNT}:objectAdmin ${INPUT_BUCKET}

gsutil iam ch serviceAccount:${SERVICE_ACCOUNT}:objectAdmin ${OUTPUT_BUCKET}

gsutil iam ch serviceAccount:${SERVICE_ACCOUNT}:objectAdmin ${ARCHIVE_BUCKET}

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member=serviceAccount:${SERVICE_ACCOUNT} --role=roles/documentai.viewer

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member=serviceAccount:${SERVICE_ACCOUNT} --role=roles/bigquery.admin

gcloud functions deploy geocode-addresses \
--region=${CLOUD_FUNCTION_LOCATION} \
--entry-point=process_address \
--runtime=python39 \
--service-account=${SERVICE_ACCOUNT} \
--source=cloud-functions/geocode-addresses \
--timeout=60 \
--env-vars-file=cloud-functions/geocode-addresses/.env.yaml \
--trigger-topic=${GEO_CODE_REQUEST_PUBSUB_TOPIC}
