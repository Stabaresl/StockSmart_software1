# src/services/google_auth.py
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import pickle

SCOPES = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]

def get_flow():
    return InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES
    )

def get_user_info(credentials):
    service = build('oauth2', 'v2', credentials=credentials)
    return service.userinfo().get().execute()