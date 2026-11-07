
from pathlib import Path

import pandas as pd
import streamlit as st

from src.tariff_engine import TariffEngine


st.set_page_config(
    page_title="EgyptPowerSim",
    page_icon="⚡",
    layout="wide",
)

# Load the electricity tariff engine.
@st.cache_resource
def load_engine():
    path = Path(__file__).resolve().parent / "config" / "tariffs.json"
    return TariffEngine.from_file(path)


engine = load_engine()

# Sidebar navigation.
with st.sidebar:
    st.title("⚡ EgyptPowerSim")
    st.caption("Household Electricity Simulator")

    page = st.radio(
        "Navigation",
        ["Dashboard", "Bill Calculator", "What-If Simulator", "About"],
    )

    st.divider()
    st.caption("MIU Graduation Project — Team AI08")


# Dashboard page.
if page == "Dashboard":
    st.title("EgyptPowerSim")
    st.subheader("Household Electricity Dashboard")

    st.write(
        "Understand your electricity consumption, estimate "
        "your monthly bill, and explore pricing scenarios."
    )

    a, b, c = st.columns(3)
    a.metric("Available Tariff Schedules", len(engine.list_schedules()))
    b.metric("Bill Calculator", "Ready")
    c.metric("AI Forecasting", "Coming Soon")

    st.info(
        "This is an early prototype. Electricity prices and "
        "service fees should be verified before official use."
    )


# Bill Calculator page.
elif page == "Bill Calculator":
    st.title("Electricity Bill Calculator")

    schedules = engine.list_schedules()
    schedule_ids = [item["id"] for item in schedules]

    selected = st.selectbox(
        "Tariff schedule",
        schedule_ids,
        format_func=lambda x: engine.get_schedule(x)["label"],
    )

    kwh = st.number_input(
        "Monthly electricity consumption (kWh)",
        min_value=0.0,
        max_value=20000.0,
        value=400.0,
        step=10.0,
    )

    include_fee = st.checkbox(
        "Include unverified service fee",
        value=False,
    )

    schedule = engine.get_schedule(selected)

    if not schedule["team_checked"]:
        st.warning(
            "This schedule has not yet been independently "
            "verified by the project team."
        )

    if st.button("Calculate Bill", type="primary"):
        result = engine.calculate_bill(
            kwh=kwh,
            schedule_id=selected,
            include_service_fee=include_fee,
        )

        st.metric(
            "Estimated Electricity Bill",
            f"{result.total_egp:,.2f} EGP",
        )

        st.subheader("Electricity Bill Breakdown")

        if result.line_items:
            df = pd.DataFrame(
                [
                    {
                        "From (kWh)": x.from_kwh,
                        "To (kWh)": x.to_kwh,
                        "Usage (kWh)": x.quantity_kwh,
                        "Rate (piastres)": x.rate_piastres,
                        "Charge (EGP)": x.amount_egp,
                    }
                    for x in result.line_items
                ]
            )

            st.dataframe(df, use_container_width=True, hide_index=True)
            st.bar_chart(
                df.set_index("To (kWh)")["Charge (EGP)"]
            )
        else:
            st.info("No electricity consumption entered.")

        st.caption(
            "Estimated energy charges based on the selected "
            "tariff. Additional charges may apply."
        )


# What-if Simulator page.
elif page == "What-If Simulator":
    st.title("What-If Electricity Simulator")

    st.write(
        "Explore how electricity costs change when consumption "
        "or electricity rates change."
    )

    kwh = st.number_input(
        "Current monthly consumption (kWh)",
        min_value=0.0,
        max_value=20000.0,
        value=400.0,
        step=10.0,
    )

    usage_change = st.slider(
        "Consumption change (%)",
        min_value=-50,
        max_value=100,
        value=0,
    )

    rate_change = st.slider(
        "Electricity unit-rate change (%)",
        min_value=-50,
        max_value=100,
        value=10,
    )

    if st.button("Compare Scenarios", type="primary"):
        scenario_kwh = min(
            20000.0,
            kwh * (1 + usage_change / 100),
        )

        original = engine.calculate_bill(kwh)
        changed = engine.calculate_bill(
            scenario_kwh,
            rate_multiplier=1 + rate_change / 100,
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Current Bill",
            f"{original.total_egp:,.2f} EGP",
        )

        col2.metric(
            "Scenario Bill",
            f"{changed.total_egp:,.2f} EGP",
        )

        difference = changed.total_egp - original.total_egp

        col3.metric(
            "Difference",
            f"{difference:+,.2f} EGP",
        )

        chart_data = pd.DataFrame(
            {
                "Scenario": ["Current", "What-If"],
                "Cost (EGP)": [
                    original.total_egp,
                    changed.total_egp,
                ],
            }
        )

        st.bar_chart(
            chart_data.set_index("Scenario")
        )

        st.caption(
            "Hypothetical scenario only. Changes in consumption "
            "may move the household into another tariff category."
        )


# About page.
elif page == "About":
    st.title("About EgyptPowerSim")

    st.write(
        "EgyptPowerSim is a graduation project at "
        "Misr International University."
    )

    st.write(
        "The project aims to help Egyptian households "
        "understand electricity bills, simulate costs, "
        "forecast consumption, and explore energy-saving options."
    )

    st.info(
        "AI forecasting, virtual household modeling, and "
        "personalized recommendations will be added later."
    )
