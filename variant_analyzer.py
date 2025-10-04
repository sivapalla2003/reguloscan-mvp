# variant_analyzer.py

import requests
import time
import numpy as np

ENSEMBL_VEP = "https://rest.ensembl.org/vep/human/id/"
CADD_API = "https://cadd.gs.washington.edu/api/v1.0/annotate"
GTEX_EQTL = "https://gtexportal.org/rest/v1/association/singleTissueEqtl"
ENSEMBL_REG = "https://rest.ensembl.org/regulatory/species/human/variant/"

def normalize(value, min_val=0, max_val=1):
    """Normalize a value into [0,1] range safely."""
    if value is None:
        return 0.0
    try:
        return max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))
    except ZeroDivisionError:
        return 0.0

def classify(score: float) -> str:
    if score >= 0.7:
        return "High"
    elif score >= 0.4:
        return "Medium"
    else:
        return "Low"

def query_ensembl_vep(rsid: str):
    url = f"{ENSEMBL_VEP}{rsid}?content-type=application/json"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

def query_cadd(rsid: str):
    try:
        r = requests.post(CADD_API, json={"ids": [rsid]}, timeout=15)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

def query_gtex(gene: str):
    """Very simplified eQTL lookup for given gene symbol."""
    url = f"{GTEX_EQTL}?geneId={gene}&tissueName=Brain_Cortex"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

def analyze_variant(rsid: str):
    """Annotate one variant with evidence scores."""
    evidence = {
        "regulatory": 0.0,
        "functional": 0.0,
        "expression": 0.0,
        "conservation": 0.0,
    }

    # --- Regulatory evidence (Regulome / Ensembl Regulatory Build) ---
    vep_data = query_ensembl_vep(rsid)
    if vep_data:
        if "regulatory_feature_consequences" in str(vep_data).lower():
            evidence["regulatory"] = 0.7  # placeholder high if regulatory element present

    # --- Functional evidence (CADD score) ---
    cadd_data = query_cadd(rsid)
    if cadd_data and "scores" in cadd_data:
        cadd = cadd_data["scores"].get(rsid, {}).get("raw", 0)
        evidence["functional"] = normalize(cadd, 0, 30)  # CADD raw typically 0–30+

    # --- Expression evidence (GTEx eQTL for affected gene) ---
    if vep_data and "transcript_consequences" in str(vep_data).lower():
        try:
            gene = vep_data[0]["transcript_consequences"][0]["gene_symbol"]
            gtex_data = query_gtex(gene)
            if gtex_data and "association" in gtex_data:
                evidence["expression"] = 0.6  # simplified: if eQTL present
        except Exception:
            pass

    # --- Conservation evidence (from VEP: phyloP / phastCons if available) ---
    if vep_data and "colocated_variants" in str(vep_data).lower():
        evidence["conservation"] = 0.5  # placeholder: need real API field

    # --- Compute overall score ---
    weights = {
        "regulatory": 0.25,
        "functional": 0.35,
        "expression": 0.25,
        "conservation": 0.15,
    }

    overall_score = sum(evidence[k] * weights[k] for k in evidence)
    label = classify(overall_score)

    return {
        "variant": rsid,
        "evidence": evidence,
        "score": overall_score,
        "priority": label,
    }


if __name__ == "__main__":
    # Quick test
    test_variant = "rs1625579"  # example schizophrenia SNP
    result = analyze_variant(test_variant)
    print(result)
