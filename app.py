import streamlit as st
import pandas as pd
import plotly.express as px
from api_functions import get_ensembl_data

st.set_page_config(page_title="ReguloSCAN", page_icon="🧬")
st.title("🧬 ReguloSCAN - Variant Prioritization")

# Input section
col1, col2 = st.columns(2)
with col1:
    variant_id = st.text_input("Single Variant ID:", placeholder="rs429358")
with col2:
    uploaded_file = st.file_uploader("Or upload CSV:", type=['csv'])

def parse_variant_data(ensembl_data):
    if not ensembl_data:
        return None
    first_result = ensembl_data[0]
    return {
        'variant_id': first_result.get('id', 'N/A'),
        'chromosome': first_result.get('seq_region_name', 'N/A'),
        'position': first_result.get('start', 'N/A'),
        'consequence': first_result.get('most_severe_consequence', 'N/A'),
    }

def calculate_priority_score(variant_info):
    score = 0
    evidence = []
    if variant_info.get('in_enhancer'):
        score += 2
        evidence.append("Enhancer region")
    if variant_info.get('cadd_score', 0) > 20:
        score += 2
        evidence.append(f"High CADD ({variant_info['cadd_score']})")
    return {
        'score': score,
        'evidence': evidence,
        'priority': 'High' if score > 4 else 'Medium' if score > 2 else 'Low'
    }

# Single variant flow
if variant_id:
    raw_data = get_ensembl_data(variant_id)
    if raw_data:
        parsed = parse_variant_data(raw_data)
        scored = calculate_priority_score(parsed)
        st.metric("Priority Score", scored['score'])
        st.write("Evidence:", ", ".join(scored['evidence']))

# Batch processing
if uploaded_file is not None:
    variants_df = pd.read_csv(uploaded_file)
    results = []
    for variant in variants_df['variant_id']:
        data = get_ensembl_data(variant)
        parsed = parse_variant_data(data)
        scored = calculate_priority_score(parsed)
        results.append({**parsed, **scored})
    results_df = pd.DataFrame(results)
    st.dataframe(results_df.sort_values('score', ascending=False))
    fig = px.bar(results_df, x='variant_id', y='score', color='priority', title='Variant Priority Scores')
    st.plotly_chart(fig)
    csv = results_df.to_csv(index=False)
    st.download_button("Download Results", csv, "variant_priorities.csv")
