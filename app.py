import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="🧬 ReguloSCAN", layout="wide")

# ===============================
# Helper: Normalize DataFrame
# ===============================
def normalize_dataframe(df):
    """Normalize dataframe columns to ensure 'Variant' and 'Score' exist if possible."""
    df.columns = [str(c).strip().lower() for c in df.columns]

    # Detect variant column
    variant_col = None
    for c in df.columns:
        if "variant" in c or "id" in c or "snp" in c:
            variant_col = c
            break

    # Detect score column
    score_col = None
    for c in df.columns:
        if "score" in c or "risk" in c or "value" in c or "prob" in c:
            score_col = c
            break

    # Fallbacks
    if variant_col is None:
        variant_col = df.columns[0]
    if score_col is None and len(df.columns) > 1:
        for c in df.columns:
            if pd.api.types.is_numeric_dtype(df[c]):
                score_col = c
                break

    # Rename
    rename_map = {}
    if variant_col: rename_map[variant_col] = "Variant"
    if score_col: rename_map[score_col] = "Score"
    df = df.rename(columns=rename_map)

    return df


# ===============================
# Helper: Analyze Variants
# ===============================
def analyze_variants(df):
    if "Score" not in df.columns:
        return None, None
    best_variant = df.loc[df["Score"].idxmax()]
    least_variant = df.loc[df["Score"].idxmin()]
    return best_variant, least_variant


# ===============================
# UI Layout
# ===============================
st.title("🧬 ReguloSCAN – Variant Analyzer")
st.write("Welcome to **ReguloSCAN**, a tool to analyze schizophrenia-associated gene variants.")
st.write("Choose one of the two options below:")

# ===============================
# Option 1: Upload Dataset
# ===============================
st.header("📂 Option 1: Upload Variant Dataset")
uploaded_file = st.file_uploader("Upload a CSV/TSV/Excel file with variant data", type=["csv", "tsv", "xlsx"])

df = None
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".tsv"):
            df = pd.read_csv(uploaded_file, sep="\t")
        else:
            df = pd.read_excel(uploaded_file)

        df = normalize_dataframe(df)

        st.success("✅ File uploaded successfully!")
        st.subheader("🔍 Preview of Variants")
        st.dataframe(df.head())

        # Best/Least
        best_variant, least_variant = analyze_variants(df)
        if best_variant is not None:
            st.markdown(f"🔥 **Best Variant:** {best_variant['Variant']} (Score: {best_variant['Score']})")
            st.markdown(f"🧊 **Least Variant:** {least_variant['Variant']} (Score: {least_variant['Score']})")

            st.subheader("📈 Statistics")
            st.write(df["Score"].describe())

            # Graphs
            st.subheader("📊 Score Distribution")
            fig, ax = plt.subplots()
            sns.histplot(df["Score"], bins=10, kde=True, ax=ax)
            st.pyplot(fig)

            st.subheader("📊 Variant Scores (Bar Chart)")
            fig, ax = plt.subplots()
            sns.barplot(x="Score", y="Variant", data=df, ax=ax)
            st.pyplot(fig)
        else:
            st.warning("⚠️ No score column detected. Showing only variants.")
    except Exception as e:
        st.error(f"❌ Error processing file: {e}")


# ===============================
# Option 2: Manual Variant Search
# ===============================
st.header("🔍 Option 2: Search Variants Manually")
variant_input = st.text_input("Enter one or more Variant IDs (comma separated, e.g., rs123, rs456):")

if st.button("Check Variants"):
    if not variant_input.strip():
        st.error("⚠️ Please enter at least one variant ID.")
    elif df is None:
        st.error("⚠️ Please upload a dataset first (Option 1).")
    else:
        query_variants = [v.strip() for v in variant_input.split(",") if v.strip()]
        found = df[df["Variant"].astype(str).isin(query_variants)] if "Variant" in df.columns else pd.DataFrame()
        not_found = [v for v in query_variants if v not in found["Variant"].astype(str).tolist()] if not found.empty else query_variants

        if not found.empty:
            st.subheader("✅ Found Variants")
            st.dataframe(found)

            if "Score" in found.columns:
                best_variant, least_variant = analyze_variants(found)
                if best_variant is not None:
                    st.markdown(f"🔥 **Best Variant:** {best_variant['Variant']} (Score: {best_variant['Score']})")
                    st.markdown(f"🧊 **Least Variant:** {least_variant['Variant']} (Score: {least_variant['Score']})")

                    st.subheader("📈 Statistics for Selected Variants")
                    st.write(found["Score"].describe())

                    st.subheader("📊 Score Distribution (Selected Variants)")
                    fig, ax = plt.subplots()
                    sns.histplot(found["Score"], bins=5, kde=True, ax=ax)
                    st.pyplot(fig)

                    st.subheader("📊 Variant Scores (Bar Chart)")
                    fig, ax = plt.subplots()
                    sns.barplot(x="Score", y="Variant", data=found, ax=ax)
                    st.pyplot(fig)

        if not_found:
            st.error(f"❌ Not found: {', '.join(not_found)}")
