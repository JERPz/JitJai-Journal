# 🚀 Project Setup & Usage Guide

Welcome! This guide will help you get your project up and running quickly on **Mac/Linux** or **Windows**. The setup scripts will take care of everything—from spinning up Docker containers to launching the Streamlit app.

---

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

* [Docker](https://www.docker.com/)
* [Python 3.8+](https://www.python.org/downloads/)
* [pip](https://pip.pypa.io/en/stable/)
* (Optional) [Streamlit](https://streamlit.io/) — will be installed via script if not available

---

## 🖥️ Running the Project

### ✅ 1. For Mac and Linux

Open your terminal and navigate to the project folder. Then run:

```bash
chmod +x run_setup.sh
./run_setup.sh
```

---

### ✅ 2. For Windows

Open **Command Prompt** or **PowerShell** in the project folder. Then run:

```bash
run_setup.bat
```

---

## ⚙️ What the Script Does

The setup script automates the following steps:

1. **Starts Docker Containers**

   * Launches a PostgreSQL database and pgAdmin for management.

2. **Creates a Virtual Environment**

   * Isolates Python dependencies inside a folder named `venv`.

3. **Installs Dependencies**

   * Automatically installs all packages from `requirements.txt`.

4. **Runs the Streamlit App**

   * Opens the application in your default web browser.

---

## 🛠️ Accessing the Database (pgAdmin)

You can manage the PostgreSQL database via the pgAdmin web interface:

* **URL**: [http://localhost:5050](http://localhost:5050)
* **Email**: `admin@jitjai.com`
* **Password**: `adminpass`

---

## 🧾 Notes

* The first run might take a few minutes as Docker pulls the required images.
* If the browser doesn’t open automatically, visit: [http://localhost:8501](http://localhost:8501)
* To stop the app and containers, press `Ctrl+C` and run:

```bash
docker-compose down
```

---
