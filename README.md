# ReguloSCAN MVP

🧬 **Non-coding Variant Prioritization Tool**

---

## Project Overview
ReguloSCAN is a tool to prioritize non-coding genetic variants based on regulatory and functional evidence. Users can input a single variant ID or upload a CSV of multiple variants to get a priority score, evidence, and visualization.

---

## Features
- Single variant input or batch CSV upload
- Fetches data from **Ensembl API**
- Calculates **priority score** based on enhancer, promoter, and CADD scores
- Displays **evidence** for the score
- Interactive **Plotly bar chart** for batch results
- CSV download for processed results

---

## Setup

1. Clone the repository or download the files.
2. Install dependencies:
```bash
pip install -r requirements.txt

Run the Streamlit app:
python -m streamlit run app.py


