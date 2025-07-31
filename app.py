
import streamlit as st
import pandas as pd
import numpy as np
from src.Opt import EnergyOptimizer
from src.helpers import create_scenario_data, calculate_financials
from pyomo.opt import SolverFactory

st.title("🔋 BaaS Optimizer – Full Model")

uploaded_file = st.file_uploader("📁 Upload Excel Input File", type=["xlsx"])

if uploaded_file:
    try:
        # Load Excel
        xls = pd.ExcelFile(uploaded_file)
        inputs_df = xls.parse("Inputs")
        load_df = xls.parse("8760_Load")

        # Create scenario
        scenario = create_scenario_data(inputs_df, load_df)

        # Run optimization
        optimizer = EnergyOptimizer(scenario)
        result = optimizer.solve()

        # Extract objective and cost
        total_cost = optimizer.model.objective.expr()

        # Display results
        st.subheader("✅ Optimization Results")
        st.write(f"**Total Optimized Energy Cost (€):** {round(total_cost(), 2)}")

        # Estimate annual savings from optimized vs baseline
        baseline_cost = np.sum(load_df["Load (kWh)"] * load_df["Grid Price (€/kWh)"])
        annual_savings = baseline_cost - total_cost()

        # Financial metrics
        inputs_dict = inputs_df.set_index("Parameter")["Value"].to_dict()
        capex = inputs_dict["Battery Capacity (kWh)"] * inputs_dict["CAPEX (€/kWh)"]
        lifetime = int(inputs_dict["Project Lifetime (years)"])
        irr_target = inputs_dict["Target IRR"]

        financials = calculate_financials(annual_savings, capex, lifetime, irr_target)

        st.subheader("📈 Financial Analysis")
        st.write({
            "Baseline Grid Cost (€/yr)": round(baseline_cost),
            "Optimized Cost (€/yr)": round(total_cost(), 2),
            "Annual Savings (€)": round(annual_savings, 2),
            "CAPEX (€)": round(capex),
            "IRR (%)": round(financials["IRR"] * 100, 2),
            "NPV (€)": round(financials["NPV"], 2),
            "Payback Period (yrs)": financials["Payback (years)"]
        })

    except Exception as e:
        st.error(f"❌ Error reading file or running model: {e}")
