# Bullying Detection System using AI

A proactive safety monitoring system built with Python and Django. This application utilizes **Artificial Intelligence (OpenAI)** and **Speech Recognition** to detect, analyze, and log verbal bullying incidents in real-time within a classroom environment.

## 📋 Features (Meeting Requirements)

### Core Functionality
* **AI-Powered Detection:** Integrates the **OpenAI API** to analyze spoken sentences for intent, aggression, and harmful context, going beyond simple keyword matching.
* **Real-Time Audio Processing:** Uses `speech_recognition` and `pydub` to continuously listen to classroom audio streams and convert speech to text on the fly.
* **Role-Based Control:**
    * **Teachers:** Initiate "Listening Mode" for their specific classes and view immediate alerts.
    * **Admins:** View global analytics (Bar/Line charts) of bullying trends over time and manage user accounts.
* **Evidence Logging:** Automatically saves timestamps, transcripts ("Detected Speech"), and audio clips of the incident for review.

### 🌟 Technical Highlights
1.  **Secure Data:** Implements `cryptography.fernet` to encrypt sensitive logs and student data.
2.  **Visual Analytics:** Dashboard includes dynamic charts showing "Bullying Events Over Time" and "Events by Classroom" for administrative oversight.
3.  **Excel Integration:** Uses `openpyxl` to export logs or import user data efficiently.
4.  **Threaded Listening:** Utilizes Python `threading` to handle audio listening tasks without blocking the main web server interface.

## 📸 Screenshots

| **Admin Dashboard** | **Real-time Listening** |
|:---:|:---:|
| ![Dashboard](screenshots/admin/ADMIN%20-%20Dashboard.png) | ![Listening](screenshots/teacher/TEACHER%20-%20Classroom%20Bullying%20Events%20-%20Listening.png) |

| **Bullying Events Log** | **User Management** |
|:---:|:---:|
| ![Events](screenshots/admin/ADMIN%20-%20Classroom%20Bullying%20Events.png) | ![Users](screenshots/admin/ADMIN%20-%20Users%20List%20Page.png) |

| **Teacher Interface** | **Login Portal** |
|:---:|:---:|
| ![Teacher](screenshots/teacher/TEACHER%20-%20Dashboard%201.png) | ![Login](LOGIN.png) |

## 🛠️ Technology Stack

* **Backend Framework:** Django (Python)
* **AI Engine:** OpenAI API (LLM for Sentiment/Intent Analysis)
* **Audio Processing:**
    * `SpeechRecognition` (STT)
    * `Pydub` (Audio manipulation)
* **Database:** MySQL
* **Security:** Cryptography (Fernet)
* **Frontend:** HTML5, CSS3, JavaScript (Chart.js)

## 🛠️ Installation

1.  **Prerequisites:**
    * Python 3.x
    * FFmpeg (Required for `pydub` audio processing).
    * MySQL Server.
    * Active OpenAI API Key.

2.  **Install Dependencies:**
    ```bash
    pip install django openai mysql-connector-python SpeechRecognition pydub cryptography openpyxl
    ```

3.  **Environment Setup:**
    * Add your OpenAI API Key in `settings.py` or `.env`.
    * Configure `DATABASES` in `settings.py` to point to your MySQL instance.

## 🚀 How to Run

1.  **Migrate Database:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```
2.  **Start Server:**
    ```bash
    python manage.py runserver
    ```
3.  **Usage:**
    * **Teacher:** Log in, select a classroom, and click **"Start Listen"**. The system will use the host microphone to monitor speech.
    * **Admin:** Log in to view statistics and manage users.

## 📝 Limitations
* **Hardware:** Requires a high-quality microphone for accurate speech-to-text conversion in a noisy classroom.
* **API Costs:** Heavy usage of the OpenAI API for analysis may incur costs.
* **Privacy:** This system is intended for safety monitoring; ensure compliance with local privacy laws regarding recording audio.

## 📂 System Roles

```json
{
    "User_Roles": [
        {
            "Role": "Administrator",
            "Access": "Full System Analytics, User Management (CRUD), Global Logs"
        },
        {
            "Role": "Teacher",
            "Access": "Start/Stop AI Listening, View Assigned Classroom Logs"
        }
    ]
}
