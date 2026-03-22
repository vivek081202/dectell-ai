# DecTell AI - Decision Intelligence Platform

<img width="801" height="430" alt="image" src="https://github.com/user-attachments/assets/cee7a736-1cba-4bf5-9ffb-6e666e6f1194"/>

<br>

> An AI-powered Business Analytics & Decision Intelligence platform built with Python and Streamlit.
> Upload any dataset, get LLM-generated insights, train ML models, simulate decisions, and chat with your data all in one place.

## 📸 Screenshots

<img width="1203" height="649" alt="image" src="https://github.com/user-attachments/assets/f894157e-3d67-4532-99d7-7d3439f11aa8" />
<img width="839" height="331" alt="image" src="https://github.com/user-attachments/assets/5a0f86c6-efd8-4dd0-b960-73487490a9de" />
<img width="897" height="501" alt="image" src="https://github.com/user-attachments/assets/a705a116-29ad-4d25-b6ae-daac504dcb7c" />

<br>

<img width="851" height="593" alt="image" src="https://github.com/user-attachments/assets/0a016348-cb7e-4ea9-a453-c00b23a36c6e" />

<img width="837" height="504" alt="image" src="https://github.com/user-attachments/assets/41c03747-d164-4861-b928-7dce7d94f9c8" />

<img width="836" height="477" alt="image" src="https://github.com/user-attachments/assets/2b9d2684-06c5-4aa4-9740-93d094fae81d" />

<img width="834" height="615" alt="image" src="https://github.com/user-attachments/assets/a56cf475-0592-405b-8aba-5a097652a017" />

<img width="826" height="567" alt="image" src="https://github.com/user-attachments/assets/8ff5858d-c2be-40e1-b67e-ed82eaf3055e" />

<img width="835" height="582" alt="image" src="https://github.com/user-attachments/assets/cbf72f76-1e71-4431-94ba-272e7bb0aaba" />

<img width="838" height="592" alt="image" src="https://github.com/user-attachments/assets/7c95c675-000d-4da1-bc68-116355c54cab" />

<img width="846" height="537" alt="image" src="https://github.com/user-attachments/assets/0fa5e70b-8715-4b8d-b45d-6b221f3ee187" />

<img width="830" height="572" alt="image" src="https://github.com/user-attachments/assets/f1867f4c-6d1b-4199-b05f-70beac15e7e2" />


## Features

| Module | Description |
|--------|-------------|
| **Smart Data Upload** | AI-driven cleaning — imputes, encodes, caps outliers only when needed |
| **Automated EDA** | Distribution charts, correlation heatmaps, LLM-generated narrative insights |
| **AI Analyze** | Business mode (plain language goals) + Technical mode (full ML control) |
| **Scenario Simulation** | What-if sliders and dropdowns for any dataset type including categoricals |
| **Causal Impact** | Difference-in-Differences with bootstrapped 95% confidence intervals |
| **Chat with Data** | Groq LLM conversational interface with full session memory |
| **Report Generator** | AI-written Business and Technical reports exportable as PDF or text |
| **Analytics Dashboard** | Live KPIs, model metrics, feature importances |
| **Developer Page** | Professional profile of the developer |

---

## Tech Stack

- **Language:** Python 3.12
- **Framework:** Streamlit
- **AI Engine:** Groq API with llama-3.3-70b-versatile
- **ML:** Scikit-learn, XGBoost
- **Data:** Pandas, NumPy
- **Visualisation:** Plotly
- **PDF Export:** ReportLab
- **Integration:** Google Sheets API

---

## Project Structure

```
dectell-ai/
├── app.py                        <- Entry point
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   ├── config.toml               <- Theme config (committed)
│   └── secrets.toml              <- NOT committed — add your keys here locally
├── assets/
│   ├── logo.png
│   ├── favicon.png
│   └── vivek_photo.jpg           <- Add your photo manually
├── pages/
│   ├── Home.py
│   ├── About.py
│   ├── Contact.py
│   ├── Upload.py
│   ├── EDA.py
│   ├── AIAnalyze.py
│   ├── Simulation.py
│   ├── Causal.py
│   ├── Chat.py
│   ├── Report.py
│   ├── Dashboard.py
│   └── Developer.py
├── modules/
│   ├── data_cleaning.py
│   ├── eda_analysis.py
│   ├── causal_analysis.py
│   └── report_generator.py
├── utils/
│   ├── data_utils.py
│   ├── model_utils.py
│   ├── llm_utils.py
│   ├── visualization_utils.py
│   ├── chat_utils.py
│   └── ui_utils.py
└── sample_datasets/
    ├── retail_sales.csv
    ├── customer_churn.csv
    ├── marketing_campaign.csv
    ├── ecommerce_transactions.csv
    ├── hr_analytics.csv
    ├── financial_timeseries.csv
    └── healthcare_patients.csv
```

---

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/dectell-ai.git
cd dectell-ai
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your secrets

Create `.streamlit/secrets.toml` locally — this file is gitignored and never pushed:

```toml
GROQ_API_KEY       = "gsk_your_groq_api_key_here"
SHEETS_WEBHOOK_URL = "https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec"
```

Get your free Groq API key at [console.groq.com](https://console.groq.com)

### 4. Run the app

```bash
streamlit run app.py
```

---

## Secrets Reference

| Key | Where to get it | Required |
|-----|----------------|----------|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) — free tier available | Yes — for all AI features |
| `SHEETS_WEBHOOK_URL` | Google Apps Script deployment URL from your spreadsheet | No — only for contact and feedback forms |

---

## Deploy on Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** and select your repo
4. Set main file as `app.py`
5. Under **Advanced settings → Secrets** paste your secrets in TOML format
6. Click **Deploy**

---

## Partner

<!-- 📸 ADD IMAGE HERE: Data & Disco Dreams Studio logo
     Save as: assets/datadisco_logo.png  then uncomment:
     ![Data & Disco Dreams Studio](assets/datadisco_logo.png) -->

**[Data & Disco Dreams Studio](https://www.datadiscodreams.com)**
Data Consulting & Design for Small Businesses | Atlanta, United States

---

## Developer

<!-- 📸 ADD IMAGE HERE: Your profile photo
     Save as: assets/vivek_photo.jpg  then uncomment:
     ![Vivek Singh](assets/vivek_photo.jpg) -->

**Vivek Singh**
MCA — Big Data & Analytics | Jaypee Institute of Information Technology, Noida

- LinkedIn: [vivek-singh-linkdin](https://www.linkedin.com/in/vivek-singh-linkdin)
- GitHub: [vivek081202](https://github.com/vivek081202)
- Email: vivekkrsingh082003@gmail.com

---

## Licence

MIT — Free to use, modify, and distribute.

---

*DecTell AI — Built with research, analytics, and intelligence.*
