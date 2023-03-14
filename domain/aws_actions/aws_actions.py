import json
import os
import boto3
import requests

from aws_lambda_powertools import Logger

logger = Logger()
appconfig = boto3.client('appconfig')


def raise_for_status(response):
    if response.status_code >= 400:
        raise Exception(
            f"There has been an exception: STATUS_CODE = {response.status_code}; MESSAGE = {response.text}")


def get_credentials_to_authenticate(client=boto3.client("secretsmanager", region_name="eu-west-2")) -> ():
    """
    This function gathers information on username and password from Security manager

    :return:
        (): username, password
    """
    secret_name = os.environ.get("SECRET_NAME")
    secret_username = os.environ.get("LOGIN_NAME")
    secret_password = os.environ.get("PASSWORD_FOR_LOGIN")
    response = client.get_secret_value(SecretId=secret_name)
    username = json.loads(response["SecretString"]).get(secret_username)
    password = json.loads(response["SecretString"]).get(secret_password)
    if username is None or "" and password is None or "":
        raise Exception(
            "There has been an error with gathering credentials to authenticate. "
            "Exception is: Username and Password can't be empty!")
    elif username is None or "":
        raise Exception("There has been an error with gathering credentials to authenticate. "
                        "Exception is: Username can't be empty!")
    elif password is None or "":
        raise Exception("There has been an error with gathering credentials to authenticate. "
                        "Exception is: Password can't be empty!")
    return username, password


def authenticate_for_hive() -> {}:
    """
    This function  runs basic authentication for Hive application

    :return:
        str : Valid Token to authenticate
    """
    credentials = get_credentials_to_authenticate()

    try:
        logger.info("Sending request to authenticate")
        headers = {
            "Content-Type": "application/json-patch+json",
        }
        requests_body = {
            "loginName": credentials[0],
            "password": credentials[1]
        }
        url = os.environ.get("AUTHENTICATION_URL")
        response = requests.post(url, headers=headers, json=requests_body)
        raise_for_status(response)
        logger.info("Authentication succeed!")
        return response.json()
    except Exception as exc:
        logger.error(f"There has been an error with Authentication! Error is: {exc}")


def send_data_to_hive(metadata):
    """
    This function sends prepared metadata to hive api

    :param
        metadata: Prepared data according to api spec
    """
    auth_resp = authenticate_for_hive()
    try:
        auth_token = auth_resp["data"]["token"]
        logger.info(f"Trying to send data with token. Data: {metadata}")

        headers = {
            "Content-Type": "application/json-patch+json",
            "Accept": "text/plain",
            "Authorization": f"Bearer {str(auth_token)}"
        }
        url = os.environ.get("UPDATE_URL")
        response = requests.put(url, headers=headers, json=metadata)
        raise_for_status(response)
        logger.info(f"Request send! Response: {response.text} Status:{response.status_code} Body sent: {metadata}")
        return {
            "status": 200,
            "body": metadata
        }
    except Exception as exc:
        logger.error(f"There has been an error with Updating data to Hive! Error is: {exc}")
