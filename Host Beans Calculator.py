import streamlit as st

# Define conversion tiers
conversion_tiers = [
    {"minBeans": 1, "maxBeans": 8, "diamondsPerBean": 0.25, "efficiency": 25.00, "fixedDiamonds": 2},
    {"minBeans": 9, "maxBeans": 109, "diamondsPerBean": 0.2661, "efficiency": 26.61, "fixedDiamonds": 29},
    {"minBeans": 110, "maxBeans": 999, "diamondsPerBean": 0.2753, "efficiency": 27.53, "fixedDiamonds": 275},
    {"minBeans": 1000, "maxBeans": 3999, "diamondsPerBean": 0.2763, "efficiency": 27.63, "fixedDiamonds": 1105},
    {"minBeans": 4000, "maxBeans": 10999, "diamondsPerBean": 0.2768, "efficiency": 27.68, "fixedDiamonds": 3045},
    {"minBeans": 11000, "maxBeans": float('inf'), "diamondsPerBean": 0.2767, "efficiency": 27.67},
]

# Tier highlight colors
tier_colors = [
    "#fecaca", "#fed7aa", "#fef08a", "#bbf7d0", "#bfdbfe", "#e9d5ff"
]

def calculate_diamonds(beans):
    if beans <= 0:
        return None

    tier = next((t for t in conversion_tiers if t["minBeans"] <= beans <= t["maxBeans"]), None)
    if not tier:
        return None

    diamonds = 0
    remainder = 0

    # Use fixed diamond amounts for specific cases
    if "fixedDiamonds" in tier and beans <= tier["maxBeans"]:
        if beans in [8, 109, 999, 3999, 10999]:
            diamonds = tier["fixedDiamonds"]
        else:
            diamonds = int(beans * tier["diamondsPerBean"])
            remainder = beans % int(1 / tier["diamondsPerBean"])
    else:
        diamonds = int(beans * tier["diamondsPerBean"])
        remainder = beans % int(1 / tier["diamondsPerBean"])

    return {
        "diamonds": diamonds,
        "remainder": remainder,
        "efficiency": tier["efficiency"],
        "diamondsPerBean": tier["diamondsPerBean"],
        "tier": conversion_tiers.index(tier) + 1
    }

# --- Streamlit UI ---

st.set_page_config(page_title="Beans to Diamonds Calculator", layout="centered")

st.title("💎 Beans to Diamonds Calculator")
st.caption("Convert your beans to diamonds with tier-based efficiency rates.")

beans_input = st.text_input("Enter number of beans", placeholder="e.g., 500")

if beans_input and beans_input.isdigit():
    beans = int(beans_input)
    result = calculate_diamonds(beans)

    if result:
        st.markdown("### 🎉 Conversion Result")
        st.success(f"**Beans:** {beans:,}")
        st.info(f"**Diamonds:** {result['diamonds']:,}")
        if result["remainder"] > 0:
            st.warning(f"Beans Remainder: {result['remainder']}")

        st.metric(label="💰 Rate", value=f"{result['diamondsPerBean']:.4f} per bean")
        st.markdown(f"**Efficiency:** "
                    f"<span style='background-color:{tier_colors[result['tier']-1]}; "
                    f"padding:4px 8px; border-radius:6px; font-weight:bold;'>"
                    f"{result['efficiency']}%</span>",
                    unsafe_allow_html=True)

# --- Tiers Table ---
st.markdown("### 📊 Conversion Tiers")

import pandas as pd
tier_table = []

for tier in conversion_tiers:
    example = f"{tier['maxBeans']:,} beans = {tier['fixedDiamonds']} diamonds" if "fixedDiamonds" in tier and tier["maxBeans"] != float('inf') else f"{tier['efficiency']}%"
    tier_table.append({
        "Beans Range": f"{tier['minBeans']} - {'∞' if tier['maxBeans'] == float('inf') else tier['maxBeans']:,}",
        "Rate": f"{tier['diamondsPerBean']:.4f}",
        "Example": example
    })

df = pd.DataFrame(tier_table)
st.dataframe(df, use_container_width=True)

# --- Tip ---
st.info("💡 **Efficiency Tip:** Higher bean amounts give better conversion rates. "
        "Efficiency increases significantly after 109 beans and reaches maximum at 4000+ beans.")
