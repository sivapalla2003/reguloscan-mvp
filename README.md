# 🧬 ReguloSCAN – Schizophrenia Variant Analyzer

This project is a **Streamlit web application** to analyze schizophrenia gene variants.  
It allows uploading a `.csv` file of variants and highlights the **best one** based on severity score.

---

## 🚀 Features
- Upload your own `.csv` variant dataset
- Automatic identification of the **most severe variant**
- Interactive visualization
- Streamlit-powered UI (easy to deploy)

---

## ⚡ Quick Start (Windows – CMD/PowerShell)

Copy and paste the following in **one window** step by step:

```powershell
# 1️⃣ Clone this repository
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

# 2️⃣ (Optional but recommended) Create a virtual environment
python -m venv venv
venv\Scripts\activate

# 3️⃣ Upgrade pip
python -m pip install --upgrade pip

# 4️⃣ Install requirements
pip install -r requirements.txt

# 5️⃣ Run the Streamlit app
python -m streamlit run app.py
