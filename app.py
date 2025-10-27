import streamlit as st
import pandas as pd
import random
import time



# 🎯 LOAD DATA

@st.cache_data
def load_data():
    df = pd.read_csv("accident_risk_predictions.csv")
    return df

df = load_data()


# 🎨 APP Configuration

st.set_page_config(page_title="Pick the Safer Road 🚗", page_icon="🚦", layout="wide")

st.title("🚘 Pick the Safer Road Game")
st.markdown("""
Test your intuition about road safety!
Two random roads will appear below can you guess which one is **safer** according to the accident prediction model?
""")




# SESSION STATE

if "round" not in st.session_state:
    st.session_state.round = 1
    st.session_state.score = 0


# HELPER FUNCTION

def decode_category(row):
    """Convert one-hot encoded columns into readable labels."""
    road_type = "Highway" if row.get("road_type_highway", 0) == 1 else \
                "Rural" if row.get("road_type_rural", 0) == 1 else \
                "Urban" if row.get("road_type_urban", 0) == 1 else "Unknown"

    lighting = "Daylight" if row.get("lighting_daylight", 0) == 1 else \
               "Dim" if row.get("lighting_dim", 0) == 1 else \
               "Night" if row.get("lighting_night", 0) == 1 else "Unknown"

    weather = "Clear" if row.get("weather_clear", 0) == 1 else \
              "Foggy" if row.get("weather_foggy", 0) == 1 else \
              "Rainy" if row.get("weather_rainy", 0) == 1 else "Unknown"

    time_of_day = "Morning" if row.get("time_of_day_morning", 0) == 1 else \
                  "Afternoon" if row.get("time_of_day_afternoon", 0) == 1 else \
                  "Evening" if row.get("time_of_day_evening", 0) == 1 else "Unknown"

    return road_type, lighting, weather, time_of_day


# ----------------------------------------------------
# GAME LOGIC (Updated)
# ----------------------------------------------------
if st.session_state.round <= 5:
    st.subheader(f"🎯 Round {st.session_state.round} of 5")

    # Pick two random roads
    road1 = df.sample(1).iloc[0]
    road2 = df.sample(1).iloc[0]

    # Decode categorical fields
    road1_type, road1_light, road1_weather, road1_time = decode_category(road1)
    road2_type, road2_light, road2_weather, road2_time = decode_category(road2)

    # Prepare two columns for display
    col1, col2 = st.columns(2)

    card_style = """
        border:2px solid #2196F3;
        border-radius:10px;
        padding:10px;
        background-color:#f0f9ff;
        font-size:16px;
        line-height:1.6;
    """

    with col1:
        st.markdown("### 🛣️ Road 1")
        st.markdown(
            f"""
            <div style='{card_style}'>
            <b>Road Type:</b> {road1_type}<br>
            <b>Curvature:</b> {round(road1['curvature'], 2)}<br>
            <b>Speed Limit:</b> {int(road1['speed_limit'] * 100)} km/h<br>
            <b>Weather:</b> {road1_weather}<br>
            <b>Time of Day:</b> {road1_time}
            </div>
            """, unsafe_allow_html=True)
        road1_btn = st.button("✅ Choose Road 1")

    with col2:
        st.markdown("### 🛣️ Road 2")
        st.markdown(
            f"""
            <div style='{card_style}'>
            <b>Road Type:</b> {road2_type}<br>
            <b>Curvature:</b> {round(road2['curvature'], 2)}<br>
            <b>Speed Limit:</b> {int(road2['speed_limit'] * 100)} km/h<br>
            <b>Weather:</b> {road2_weather}<br>
            <b>Time of Day:</b> {road2_time}
            </div>
            """, unsafe_allow_html=True)
        road2_btn = st.button("✅ Choose Road 2")

    safer = 1 if road1['predicted_accident_risk'] < road2['predicted_accident_risk'] else 2
    risk1 = round(road1['predicted_accident_risk'], 3)
    risk2 = round(road2['predicted_accident_risk'], 3)

    if road1_btn or road2_btn:
        if (road1_btn and safer == 1) or (road2_btn and safer == 2):
            st.success(f"🎉 Correct! The model agrees — Road {safer} was safer. "
                    f"(Predicted risks: Road 1 = {risk1}, Road 2 = {risk2})")
            st.session_state.score += 1
        else:
            st.warning(f"😅 Not quite! The model predicted **Road {safer}** as safer "
                    f"(Predicted risks: Road 1 = {risk1}, Road 2 = {risk2}).")

    # Show Next Round or Finish button depending on progress
    if st.session_state.round < 5:
        if st.button("➡️ Next Round"):
            st.session_state.round += 1
            st.rerun()
    else:
        if st.button("🏁 See Final Score"):
            st.session_state.round += 1  # push past 5 to trigger Game Over
            st.rerun()



# GAME OVER SCREEN

else:
    st.balloons()
    st.header("🎊 Game Over!")
    st.subheader(f"Your Final Score: **{st.session_state.score}/5** 🚗💨")

    if st.session_state.score == 5:
        st.success("🏆 Perfect! You're a road safety expert!")
    elif st.session_state.score >= 3:
        st.info("😎 Great job! You have a good sense of safe roads.")
    else:
        st.warning("🚦 Better luck next time — stay alert on the road!")

    if st.button("🔁 Play Again"):
        st.session_state.round = 1
        st.session_state.score = 0
        st.rerun()
