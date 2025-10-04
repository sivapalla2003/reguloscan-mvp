# app.py
import streamlit as st
import pandas as pd
import time
import plotly.express as px

from variant_analyzer import analyze_variant

st.set_page_config(page_title="ReguloSCAN", layout="wide")

st.title("🧬 ReguloSCAN - Variant Prioritization Dashboard")

# File uploader
uploaded_file = st.file_uploader("Upload a CSV file with variants", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Check required column
    if "Variant" not in df.columns:
        st.error("CSV must contain a column named 'Variant'")
    else:
        start = time.time()

        results = []
        for rsid in df["Variant"]:
            try:
                result = analyze_variant(str(rsid))
                results.append(result)
            except Exception as e:
                results.append({
                    "variant": rsid,
                    "evidence": {"regulatory": 0, "functional": 0, "expression": 0, "conservation": 0},
                    "score": 0,
                    "priority": "Error"
                })

        # Convert results into DataFrame
        results_df = pd.DataFrame([{
            "Variant": r["variant"],
            "Score": round(r["score"], 3),
            "Priority": r["priority"],
            "Regulatory": r["evidence"]["regulatory"],
            "Functional": r["evidence"]["functional"],
            "Expression": r["evidence"]["expression"],
            "Conservation": r["evidence"]["conservation"],
        } for r in results])

        # --- Summary Cards ---
        total = len(results_df)
        high = (results_df["Priority"] == "High").sum()
        medium = (results_df["Priority"] == "Medium").sum()
        low = (results_df["Priority"] == "Low").sum()
        runtime = round(time.time() - start, 2)

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Variants", total)
        c2.metric("High Priority", high)
        c3.metric("Medium Priority", medium)
        c4.metric("Low Priority", low)
        c5.metric("Runtime (s)", runtime)

        # --- Charts ---
        st.subheader("📊 Variant Distribution")

        dist = results_df["Priority"].value_counts().reset_index()
        dist.columns = ["Priority", "Count"]
        bar_fig = px.bar(dist, x="Priority", y="Count", color="Priority", text="Count")
        st.plotly_chart(bar_fig, use_container_width=True)

        st.subheader("🧪 Evidence Contribution (Average)")
        avg_evidence = results_df[["Regulatory","Functional","Expression","Conservation"]].mean().reset_index()
        avg_evidence.columns = ["Evidence", "Score"]
        pie_fig = px.pie(avg_evidence, values="Score", names="Evidence", title="Evidence Contribution")
        st.plotly_chart(pie_fig, use_container_width=True)

        # --- Results Table ---
        st.subheader("📑 Results Table")
        st.dataframe(results_df, use_container_width=True)

        # Download button
        csv_out = results_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Results", csv_out, "variant_results.csv", "text/csv")
