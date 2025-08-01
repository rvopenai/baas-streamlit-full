
import pandas as pd
import numpy_financial as npf
import os

def create_scenario_data(folder):
    load = pd.read_csv(os.path.join(folder, "load.csv"))["Load (kWh)"].tolist()
    pv = pd.read_csv(os.path.join(folder, "pv.csv"))["PV (kWh)"].tolist()
    ev = pd.read_csv(os.path.join(folder, "ev.csv"))["EV (kWh)"].tolist()
    price = pd.read_csv(os.path.join(folder, "price.csv"))["Grid Price (€/kWh)"].tolist()

    return {
        "load": load,
        "pv": pv,
        "ev": ev,
        "price": price,
        "battery_capacity": 200,
        "battery_power": 50,
        "eta_ch": 0.95,
        "eta_dis": 0.95
    }

def calculate_financials(annual_savings, capex, lifetime, irr_target):
    cash_flows = [-capex] + [annual_savings] * lifetime
    irr = npf.irr(cash_flows)
    npv = npf.npv(irr_target, cash_flows)
    payback = next((i for i, v in enumerate(cash_flows[1:], 1)
                    if sum(cash_flows[:i + 1]) >= 0), None)
    return {"IRR": irr, "NPV": npv, "Payback (years)": payback}
