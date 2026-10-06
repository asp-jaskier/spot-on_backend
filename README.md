# SpotOn


# ⚙️ Environment Configuration

The platform requires several environment variables for authentication and system configuration.

Create a file named:

```
.env
```

Example configuration:

```
URL_DATABASE="postgresql://postgres:hasło_do_db@localhost:5432/spoton"

SECRET_KEY=''
ALGORITM='HS256'
PASSWORD_EMAIL='password_for_your_email'
SMTP_SERVER_EMAIL='email'
```

⚠️ Never share or publicly expose your `.env` configuration file.