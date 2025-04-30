import httpx
import requests
# BASE_URL = "https://shark-app-6wiyn.ondigitalocean.app/api/v1"
# BASE_URL='https://api.neovis.io/api/v1'
# LOGIN_ENDPOINT = f"{BASE_URL}/auth/login"
# TASK_ENDPOINT = f"{BASE_URL}/tasks/{{id}}"

#LOGIN_PAYLOAD = {"email": "newAI@gmail.com", "password": "@test#123"}



# def fetch_task_by_id(task_id: int,token:str) -> dict:
#     """
#     Logs in to get the token and fetches the task details by ID (Synchronous).
#     """
    
#     login_response = requests.post(LOGIN_ENDPOINT)
#     if login_response.status_code != 201:
#         raise ValueError(
#             f"Login failed: {login_response.status_code} {login_response.text}"
#         )

#     token = login_response.json().get("token")
#     print("token",token)
#     if not token:
#         raise ValueError("Token not found in login response.")

    
#     headers = {"Authorization": f"Bearer {token}"}
#     task_response = requests.get(TASK_ENDPOINT.format(id=task_id), headers=headers)
#     if task_response.status_code != 200:
#         raise ValueError(
#             f"Failed to fetch task: {task_response.status_code} {task_response.text}"
#         )

  
# #     return task_response.json()
# def fetch_task_by_id(task_id: int, token: str) -> dict:
#     """
#     Fetches the task details by ID using the token passed from frontend.
#     """

#     if not token:
#         raise ValueError("Token not provided.")

#     headers = {"Authorization": f"Bearer {token}"}
#     task_response = requests.get(TASK_ENDPOINT.format(id=task_id), headers=headers)

#     if task_response.status_code != 200:
#         raise ValueError(
#             f"Failed to fetch task: {task_response.status_code} {task_response.text}"
#         )

#     return task_response.json()



#########################################################################################################






from fastapi import FastAPI, Query
import requests
import os
from dotenv import load_dotenv
from enum import Enum

load_dotenv()

# Fetching BASE_URLs from environment variables
BASE_URL_DEV = os.getenv('BASE_URL_DEV')
BASE_URL_PROD = os.getenv('BASE_URL_PROD')
BASE_URL_UAT = os.getenv('BASE_URL_UAT') # UAT-க்கான URL-ஐயும் எடுக்குறோம்

class Environment(Enum):
    DEV = "Development"
    PROD = "Production"
    UAT = "Uat"

def get_base_url(env: Environment):
    if env == Environment.PROD:
        url = BASE_URL_PROD
    elif env == Environment.UAT:
        url = BASE_URL_UAT
    else: # Default to DEV
        url = BASE_URL_DEV
    print(f"get_base_url called with env: {env}, returning URL: {url}")
    return url



# The function to fetch task by ID
def fetch_task_by_id(task_id: int, token: str, env: Environment = Query(Environment.DEV)) -> dict:
    """
    Fetches the task details by ID using the token passed from frontend.
    The base URL will change depending on the selected `env` (dev, prod, uat).
    """

    if not token:
        raise ValueError("Token not provided.")

    # Select the correct base URL based on the environment
    base_url = get_base_url(env)

    # Define the endpoints using the base URL
    TASK_ENDPOINT = f"{base_url}/tasks/{{id}}"

    headers = {"Authorization": f"Bearer {token}"}

    # Make the GET request to fetch task data by ID
    task_response = requests.get(TASK_ENDPOINT.format(id=task_id), headers=headers)
    print(f"fetched this url: {task_response.url}")

    # If the request fails, raise an error
    if task_response.status_code != 200:
        raise ValueError(
            f"Failed to fetch task for {env.value}: {task_response.status_code} {task_response.text}"
        )

    # Return the task data as JSON
    return task_response.json()