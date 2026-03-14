import streamlit as st
import json
import subprocess

st.set_page_config(page_title="🛸 UFO Crypto Radar", layout="wide")

st.title("🛸 UFO Crypto Radar")

# load signals
with open("signals.json") as f:
    signals = json.load(f)

st.subheader("👽 Alien Signal Board")

for s in signals:

    col1, col2 = st.columns([3,1])

    col1.write(f"🛸 {s['symbol']}  |  {s['type']}")

    if col2.button(f"Analyze {s['symbol']}"):
        output = subprocess.check_output(
            ["python","deep_scan.py",s["symbol"]]
        ).decode()

        st.text(output)
