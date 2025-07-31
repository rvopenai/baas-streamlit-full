
import pandas as pd
import numpy_financial as npf

def create_scenario_data(inputs_df, load_df):
    # Extract values from inputs DataFrame
    inputs = inputs_df.set_index("Parameter")["Value"].to_dict()

    scenario = {
        "battery_capacity": inputs["Battery Capacity (kWh)"],
        "battery_power": inputs["Power (kW)"],
        "eta_ch": 0.95,
        "eta_dis": 0.95,
        "load": load_df["Load (kWh)"].tolist(),
        "pv": [0.0] * len(load_df),
        "price": load_df["Grid Price (€/kWh)"].tolist()
    }
    return scenario

def calculate_financials(annual_savings, capex, lifetime, irr_target):
    cash_flows = [-capex] + [annual_savings] * lifetime
    irr = npf.irr(cash_flows)
    npv = npf.npv(irr_target, cash_flows)
    payback = next((i for i, v in enumerate(cash_flows[1:], 1)
                    if sum(cash_flows[:i + 1]) >= 0), None)
    return {"IRR": irr, "NPV": npv, "Payback (years)": payback}
