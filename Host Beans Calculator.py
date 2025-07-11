import streamlit as st
import pandas as pd
from io import BytesIO

# Tiered salary structure
TIERED_SALARY = [
    (100_000, 80),
    (70_000, 70),
    (50_000, 60),
    (30_000, 50),
    (20_000, 40),
    (10_000, 30),
    (5_000, 23),
    (0, 0)
]

def get_salary_usd(beans_earned):
    for threshold, salary in TIERED_SALARY:
        if beans_earned >= threshold:
            return salary
    return 0

def calculate_total_beans(beans_earned):
    salary_usd = get_salary_usd(beans_earned)
    salary_beans = salary_usd * 210
    commission = beans_earned * 0.05
    total = salary_beans + commission
    return salary_usd, salary_beans, commission, total

st.set_page_config(page_title="Agent Bean Calculator", layout="centered")
st.title("🎯 Agent Bean Calculator")

with st.form("bean_calc_form"):
    num_agents = st.number_input("How many agents?", min_value=1, step=1)
    agents_input = []
    for i in range(int(num_agents)):
        st.markdown(f"#### Agent {i+1}")
        name = st.text_input("Name", key=f"name_{i}")
        beans_earned = st.number_input("Beans Earned by Host", key=f"beans_{i}", min_value=0)
        agents_input.append({"name": name, "beans_earned": beans_earned})
    submitted = st.form_submit_button("Calculate")

if submitted:
    results = []
    for agent in agents_input:
        salary_usd, salary_beans, commission, total = calculate_total_beans(agent["beans_earned"])
        results.append({
            "Agent": agent["name"],
            "Beans Earned": agent["beans_earned"],
            "Salary (USD)": salary_usd,
            "Salary in Beans": salary_beans,
            "5% Commission": commission,
            "Total Beans": total
        })
    df = pd.DataFrame(results)
    st.success("✅ Calculations complete!")
    st.dataframe(df)

    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    st.download_button(
        "📥 Download Excel File",
        data=buffer.getvalue(),
        file_name="agent_beans_summary.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
