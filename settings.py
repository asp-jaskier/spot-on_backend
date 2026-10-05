import os
from dotenv import load_dotenv

load_dotenv()
algorithm = str(os.getenv("ALGORITHM"))
secret_key_token = str(os.getenv("SECRET_KEY"))

stage = str(os.getenv("STAGE"))

url_database = os.getenv("URL_DATABASE")
password_email = str(os.getenv("PASSWORD_EMAIL"))
smtp_server_email = str(os.getenv("SMTP_SERVER_EMAIL"))

class static_vars():
    examples_file_path = "data/examples.txt"
    learning_files_path = "data/learning/"