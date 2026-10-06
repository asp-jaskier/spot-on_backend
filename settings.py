import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
algorithm = str(os.getenv("ALGORITHM"))
secret_key_token = str(os.getenv("SECRET_KEY"))

stage = str(os.getenv("STAGE"))

url_database = os.getenv("URL_DATABASE")
password_email = str(os.getenv("PASSWORD_EMAIL"))
smtp_server_email = str(os.getenv("SMTP_SERVER_EMAIL"))

class static_vars():
    access_expires = 15 # minutes
    refresh_expires = 3 # hours
    radius_km_loading = 18
    spots_photos_path = Path('data/photos/spots')

# spots_photos_path.mkdir(parents=True, exist_ok=True) dodać potem zeby działało