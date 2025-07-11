# save this as beans_to_diamonds_app.py

import streamlit as st

def get_conversion_rate(beans):
    # Tiered conversion rates based on the image
    tiers = [
        (8, 0.25),
        (109, 0.2661),
        (999, 0.2753),
        (3999, 0.2763),
        (10999, 0.2768)
    ]
    
    # Sort tiers to handle in order
    tiers.sort()
    
    for i in range(len(tiers)):
        if beans <= tiers[i][0]:
            return tiers[i][1]
    
    # If beans > highest tier
    return tiers[-1][1]

def beans_to_diamonds(beans):
    rate = get_conversion_rate(beans)
    diamonds = beans * rate
    return diamonds, rate

# Streamlit UI
st.title("💎 Beans to Diamonds Calculator")

beans_input = st.number_input("Enter number of beans:", min_value=1, step=1)

if beans_input:
    diamonds, rate = beans_to_diamonds(beans_input)
    st.success(f"Conversion Rate: {rate:.4f} diamonds per bean")
    st.metric(label="Estimated Diamonds Received", value=f"{diamonds:.2f}")
