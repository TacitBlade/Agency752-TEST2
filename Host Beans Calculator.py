import streamlit as st
import pandas as pd
from io import BytesIO

# Tiered salary structure
TIERED_SALARY = [
    
(6000000, 10200),
(5000000, 9200),
(4000000, 7650),
(3000000, 5900),
(2000000, 3925),
(1500000, 2950),
(1000000, 2000),
(800000, 1613),
(600000, 1220),
(450000, 945),
(350000, 735),
(250000, 525),
(170000, 361),
(130000, 281),
(120000, 263),
(110000, 243),
(100000, 221),
(90000, 200),
(80000, 178),
(70000, 156),
(60000, 134),
(50000, 112),
(40000, 89),
(30000, 67),
(20000, 45),
(10000, 23),
(5000, 23),
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
