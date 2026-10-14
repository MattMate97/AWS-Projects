import json
import urllib.parse
import boto3

s3 = boto3.client("s3")
rekognition = boto3.client("rekognition")


def lambda_handler(event, context):
    record = event["Records"][0]["s3"]
    bucket = record["bucket"]["name"]
    key = urllib.parse.unquote_plus(record["object"]["key"])

    # Only process files in uploads/, so results never retrigger this function
    if not key.startswith("uploads/"):
        return {"skipped": key}

    response = rekognition.detect_labels(
        Image={"S3Object": {"Bucket": bucket, "Name": key}},
        MaxLabels=10,
        MinConfidence=80,
    )

    labels = [
        {"name": label["Name"], "confidence": round(label["Confidence"], 2)}
        for label in response["Labels"]
    ]

    filename = key.split("/", 1)[1].rsplit(".", 1)[0]
    result_key = f"results/{filename}.json"

    s3.put_object(
        Bucket=bucket,
        Key=result_key,
        Body=json.dumps({"image": key, "labels": labels}, indent=2),
        ContentType="application/json",
    )
    return {"result": result_key, "labels": len(labels)}