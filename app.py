
import streamlit as st
import pandas as pd
import numpy as np
import os
import tempfile
from src.Opt import EnergyOptimizer
from src.helpers import create_scenario_data, calculate_financials

st.title("🔋 BaaS Optimizer – Full Model (Multi-File Upload)")

st.markdown("Upload your 4 required CSV files: `load.csv`, `pv.csv`, `ev.csv`, and `price.csv`")

uploaded_files = st.file_uploader("📁 Upload Files", accept_multiple_files=True, type="csv")

if uploaded_files and len(uploaded_files) == 4:
    with tempfile.TemporaryDirectory() as temp_dir:
        filenames = []

        for f in uploaded_files:
            path = os.path.join(temp_dir, f.name)
            with open(path, "wb") as out_file:
                out_file.write(f.read())
            filenames.append(f.name)

        expected_files = {"load.csv", "pv.csv", "ev.csv", "price.csv"}
        if expected_files.issubset(set(filenames)):
            # Load scenario from uploaded files
            scenario = create_scenario_data(temp_dir)

            optimizer = EnergyOptimizer(scenario)
            result = optimizer.solve()

            cost = optimizer.model.objective.expr()

            st.subheader("✅ Optimization Result")
            st.write(f"**Total Optimized Energy Cost (€)**: {round(cost(), 2)}")

            # Assumptions (placeholder values, can be extended)
            capex = scenario["battery_capacity"] * 300  # €/kWh × capacity
            lifetime = 10
            irr_target = 0.10
            baseline_cost = np.sum(scenario["load"]) * np.mean(scenario["price"])
            savings = baseline_cost - cost()

            financials = calculate_financials(savings, capex, lifetime, irr_target)

            st.subheader("📈 Financial Analysis")
            st.write({
                "Baseline Grid Cost (€/yr)": round(baseline_cost),
                "Optimized Cost (€/yr)": round(cost(), 2),
                "Annual Savings (€)": round(savings, 2),
                "CAPEX (€)": round(capex),
                "IRR (%)": round(financials["IRR"] * 100, 2),
                "NPV (€)": round(financials["NPV"], 2),
                "Payback Period (yrs)": financials["Payback (years)"]
            })
        else:
            st.error("❌ Please upload all 4 required files: load.csv, pv.csv, ev.csv, and price.csv")
else:
    st.info("Upload all 4 files to begin.")
