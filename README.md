# 🚗 SpotOn — Backend

> The backend API powering **SpotOn**, a platform for car spotting, automotive events, and connecting car enthusiasts.

[![Platform](https://img.shields.io/badge/platform-automotive-red)]()
[![Language](https://img.shields.io/badge/language-Python-blue)]()
[![Framework](https://img.shields.io/badge/framework-FastAPI-009688)]()
[![Database](https://img.shields.io/badge/database-PostgreSQL-336791)]()
[![Status](https://img.shields.io/badge/status-in%20development-orange)]()

---

# ✨ Overview

**SpotOn Backend** is the server-side component of the SpotOn platform. It provides the API and database integration needed to support the application's core functionality.

The backend is responsible for processing requests, managing application data, handling authentication, and providing the foundation for communication between the frontend and the database.

SpotOn aims to bring car spotting, automotive photography, and event discovery together in one place.

---

# 🎯 Purpose

The purpose of the backend is to provide a centralized API for managing SpotOn's application data and business logic.

It serves as the foundation for features such as:

- 📸 Car spotting and vehicle information.
- 👤 User accounts and authentication.
- 🗺️ Automotive events and location-based discovery.
- 📝 Event registration.
- 📧 Email-related functionality.
- 🔗 Communication between the frontend and backend services.

---

# 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming language |
| FastAPI | API development |
| PostgreSQL | Relational database |
| SQLAlchemy | Database interaction |
| JWT | Token-based authentication |
| SMTP | Email functionality |

---

# 🏗️ Architecture

The backend acts as the central layer between the SpotOn frontend and the database.

```text
          SpotOn Frontend
                 │
                 ▼
             FastAPI
                 │
       ┌─────────┼─────────┐
       ▼         ▼         ▼
 Authentication  Routes  Validation
       │         │         │
       └─────────┼─────────┘
                 ▼
           Database Layer
                 │
                 ▼
             PostgreSQL
```

The API processes incoming requests, validates data, applies application logic, and interacts with PostgreSQL to retrieve or persist information.

---

# 📂 Project Structure

The repository is organized into modules for routing, validation, database access, and application configuration.

```text
spot-on_backend/
├── routes/          # API endpoints and route handlers
├── schemas/         # Request and response schemas
├── utils/           # Shared utility functions
├── database.py      # Database connection and configuration
├── models.py        # Database models
├── settings.py      # Application settings
├── main.py          # Application entry point
├── requirements.txt # Python dependencies
├── .gitignore
└── README.md
```

---

# 🚀 Getting Started

Follow these steps to run the backend locally.

## Prerequisites

Make sure you have installed:

- Python 3.10 or newer, compatible with the project dependencies.
- PostgreSQL.
- Git.
- pip.

## 1. Clone the repository

```bash
git clone https://github.com/asp-jaskier/spot-on_backend.git
cd spot-on_backend
```

## 2. Create a virtual environment

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

## 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Configure environment variables

Create a `.env` file in the project root directory and configure the required variables.

See the [Environment Configuration](#-environment-configuration) section below.

## 5. Start the application

Run the FastAPI application using Uvicorn:

```bash
uvicorn main:app --reload
```

The `main:app` command assumes that `main.py` exposes a FastAPI instance named `app`.

Once the server starts, the API will usually be available at:

- API base URL: `http://127.0.0.1:8000`
- Interactive Swagger documentation: `http://127.0.0.1:8000/docs`
- Alternative API documentation: `http://127.0.0.1:8000/redoc`

The documentation URLs are available when the corresponding FastAPI documentation endpoints are enabled.

---

# ⚙️ Environment Configuration

The backend requires environment variables for database connectivity, authentication, and email functionality.

Create a file named:

```text
.env
```

Example configuration:

```env
URL_DATABASE="postgresql://postgres:your_database_password@localhost:5432/spoton"

SECRET_KEY="your_secret_key"
ALGORITM="HS256"

PASSWORD_EMAIL="password_for_your_email"
SMTP_SERVER_EMAIL="email"
```

## Environment Variables

| Variable | Description |
|---|---|
| `URL_DATABASE` | PostgreSQL connection URL used by the application. |
| `SECRET_KEY` | Secret key used for authentication and cryptographic operations. |
| `ALGORITM` | JWT signing algorithm configured by the application. |
| `PASSWORD_EMAIL` | Password or application password used for email functionality. |
| `SMTP_SERVER_EMAIL` | Email account or SMTP identity configured by the application. |

Replace the example values with your own local configuration.

### Database Configuration

Make sure PostgreSQL is running and that the specified database exists.

For example, the connection URL follows this format:

```text
postgresql://USERNAME:PASSWORD@HOST:PORT/DATABASE_NAME
```

If your database password contains special characters, URL-encode them where required by the connection URL format.

### Security

- Never commit your `.env` file to version control.
- Use a strong, randomly generated `SECRET_KEY`.
- Never use production credentials in public examples.
- Keep email credentials private.
- Use environment variables or a secret manager for production deployments.

Ensure that `.env` is included in `.gitignore`.

---

# 🔐 Authentication

SpotOn uses a secret key and a configured JWT signing algorithm for its authentication-related functionality.

The backend's authentication layer is intended to support secure communication between the client and protected API endpoints.

Authentication configuration is provided through environment variables rather than hardcoded credentials.

---

# 🗺️ SpotOn Platform Integration

The backend supports the development of a broader automotive platform.

Potential areas of integration include:

### Car Spotting

- Store and retrieve spotted vehicle information.
- Associate vehicle records with users.
- Support vehicle brands, models, and photographs.

### Automotive Events

- Manage event information.
- Provide event data to the frontend.
- Support event registration workflows.
- Supply event information for map-based discovery.

### Community Features

- Support user profiles and community interactions.
- Provide a foundation for future group chats.
- Enable future achievement and quest systems.

---

# 🛣️ Roadmap

Planned backend improvements and platform integrations include:

- [ ] Expand vehicle brand and model data.
- [ ] Support a car Pokédex and personal vehicle collections.
- [ ] Extend automotive event management and registration.
- [ ] Improve authentication and authorization.
- [ ] Add support for group chats and messaging.
- [ ] Implement daily quests and progress tracking.
- [ ] Add achievements, experience points, and leaderboards.
- [ ] Improve API testing and automated validation.
- [ ] Add deployment documentation and production configuration.

Features in this roadmap may not yet be implemented.

---

# 🧪 Development

When contributing to the backend, keep the following principles in mind:

- Keep route handlers organized and maintainable.
- Validate incoming request data.
- Keep credentials outside the source code.
- Handle database errors appropriately.
- Test changes before submitting them.
- Document new environment variables and API behavior.

---

# 🤝 Contributing

Contributions and suggestions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Implement and test your changes.
4. Commit your changes with a descriptive message.
5. Open a pull request explaining your improvements.

For larger changes, open an issue first to discuss the proposed solution.

---

# 📄 License

A license has not yet been specified. Until a license is added to the repository, permission to reuse, modify, or redistribute the project should not be assumed.

---

<p align="center">
  <strong>SpotOn Backend — Powering every spot. 🚗</strong>
</p>
