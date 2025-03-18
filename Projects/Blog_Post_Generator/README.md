# LangChain Image Generation Project

This project uses **LangChain** with **Google Cloud Vertex AI** to generate images from text prompts.

---

## 🚀 **Setup Instructions**

### ✅ **1. Clone the repository**
```bash
git clone <repo-url>
cd <your-project-folder>
```

### ✅ **2. Create a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

### ✅ **3. Install dependencies**
```bash
pip install -r requirements.txt
```

---

## 🔥 **4. Google Cloud Setup**

### 🛠️ **GCP Authentication**
1. Create a **service account key** from the GCP Console.
2. Download the JSON key file.
3. Place the key file in your project directory.
4. Authenticate:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-key.json"
gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS"
```

5. Set the project and region:
```bash
gcloud config set project <your-gcp-project-id>
gcloud config set compute/region us-central1
```

---

## ⚙️ **Run the Project**
```bash
python parallel_chain.py
```

---

## 🛠️ **Environment Variables**
Ensure you have the following environment variables configured:
```bash
GOOGLE_APPLICATION_CREDENTIALS=<path_to_your_service_account_key.json>
```

---

## 🔧 **Dependencies**
- Python 3.x
- LangChain
- Google Cloud Vertex AI
- Pillow (for image processing)
- dotenv (for environment variables)

---

## 🛠️ **API Enablement**
Make sure the **Vertex AI API** is enabled:
```bash
gcloud services enable aiplatform.googleapis.com
```

---

## 🛡️ **Troubleshooting**
- If you get `403 PermissionDenied`, make sure the **Vertex AI API** is enabled.
- If the `GOOGLE_APPLICATION_CREDENTIALS` path is incorrect, re-export the variable:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/correct/path/to/key.json"
```

