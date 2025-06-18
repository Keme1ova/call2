# firebase_config.py

import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
import base64
import os
import json

# Получаем ключ из переменной окружения
encoded_key = os.environ["FIREBASE_KEY_BASE64"]
decoded_key = base64.b64decode(encoded_key)
key_dict = json.loads(decoded_key)

cred = credentials.Certificate(key_dict)
firebase_admin.initialize_app(cred)

auth = firebase_auth  # экспортируем
