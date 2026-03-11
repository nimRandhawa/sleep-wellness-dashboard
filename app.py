import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# -------------------------
# Data Logic
# -------------------------
def load_data():
    try:
        df = pd.read_csv("data.csv")
        df["date"] = pd.to_datetime(df["date"])
    except FileNotFoundError:
        data = {
            "date": pd.date_range(start="2024-01-01", periods=7),
            "sleep_hours": [7, 6.5, 8, 5.5, 7.5, 8.2, 7.8],
            "mood": [4, 3, 5, 2, 4, 5, 4],
            "productivity": [3, 4, 5, 2, 4, 5, 4],
            "caffeine": [2, 3, 1, 4, 2, 1, 1],
            "screen_time": [4, 6, 3, 7, 4, 2, 3]
        }
        df = pd.DataFrame(data)
    return df.sort_values("date")

def generate_sleep_stages(total_hours):
    intervals = int(total_hours * 4)
    start_time = datetime.strptime("22:30", "%H:%M")

    times = [
        (start_time + timedelta(minutes=15*i)).strftime("%H:%M")
        for i in range(intervals)
    ]

    cycle = [1, 3, 4, 4, 3, 2, 3]
    stages = (cycle * (intervals // len(cycle) + 1))[:intervals]

    return pd.DataFrame({"Time": times, "Stage": stages})

# -------------------------
# Page Setup
# -------------------------
st.set_page_config(page_title="Sleep Aura", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Lexend', sans-serif;
    background-color: #0f172a;
}

.main {
    background: linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%);
}

div[data-testid="stMetric"] {
    background-color: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    padding: 15px;
    border-radius: 15px;
}

div[data-testid="stMetricValue"] {
    color: #818cf8;
}

</style>
""", unsafe_allow_html=True)

df = load_data()
latest = df.iloc[-1]

# -------------------------
# Sleep Score Logic
# -------------------------
sleep_score = min(
    100,
    int(
        latest["sleep_hours"] * 10
        + latest["mood"] * 6
        + latest["productivity"] * 6
        - latest["caffeine"] * 3
        - latest["screen_time"] * 2
    )
)

readiness = max(0, sleep_score - (abs(8 - latest["sleep_hours"]) * 5))

# -------------------------
# Header
# -------------------------
st.title("🌙 Sleep Aura Wellness")
st.write(f"Reflecting on your rest for **{latest['date'].strftime('%A, %b %d')}**")

# -------------------------
# Top Section
# -------------------------
col_main, col_stages = st.columns([1,1.5])

with col_main:

    fig_score = go.Figure(go.Indicator(
        mode="gauge+number",
        value=sleep_score,
        title={'text':"Sleep Quality"},
        gauge={
            'axis':{'range':[0,100]},
            'bar':{'color':"#818cf8"},
            'steps':[
                {'range':[0,50],'color':'rgba(239,68,68,0.1)'},
                {'range':[50,80],'color':'rgba(245,158,11,0.1)'},
                {'range':[80,100],'color':'rgba(16,185,129,0.1)'}
            ]
        }
    ))

    fig_score.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color':"white"},
        height=350
    )

    st.plotly_chart(fig_score, use_container_width=True)

with col_stages:

    stages_df = generate_sleep_stages(latest["sleep_hours"])

    fig_stages = px.line(
        stages_df,
        x="Time",
        y="Stage",
        line_shape="hv",
        title="Sleep Architecture (Hypnogram)"
    )

    fig_stages.update_traces(
        line_color='#818cf8',
        fill='toself',
        fillcolor='rgba(129,140,248,0.1)'
    )

    fig_stages.update_layout(
        yaxis=dict(
            tickmode='array',
            tickvals=[1,2,3,4],
            ticktext=["Awake","REM","Light","Deep"],
            autorange="reversed"
        ),
        template="plotly_dark",
        height=350
    )

    st.plotly_chart(fig_stages, use_container_width=True)

# -------------------------
# Metrics
# -------------------------
m1,m2,m3,m4 = st.columns(4)

m1.metric("Readiness", f"{int(readiness)}%")
m2.metric("Sleep Hours", f"{latest['sleep_hours']}h")
m3.metric("Caffeine", f"{latest['caffeine']} cups")
m4.metric("Screen Time", f"{latest['screen_time']}h")

st.divider()

# -------------------------
# Trends
# -------------------------
left_col,right_col = st.columns([2,1])

with left_col:

    st.subheader("7-Day Sleep Trend")

    fig_trend = px.area(
        df.tail(7),
        x="date",
        y="sleep_hours",
        markers=True
    )

    fig_trend.update_traces(
        line_color='#10b981',
        fillcolor='rgba(16,185,129,0.1)'
    )

    fig_trend.update_layout(
        template="plotly_dark",
        height=300
    )

    st.plotly_chart(fig_trend, use_container_width=True)

# -------------------------
# Logging
# -------------------------
with right_col:

    st.subheader("Log Entry")

    with st.expander("Add Today's Stats"):

        with st.form("entry_form"):

            d = st.date_input("Date", datetime.now())
            sh = st.slider("Sleep Hours",0.0,12.0,7.5)
            md = st.slider("Mood",1,5,3)
            pr = st.slider("Productivity",1,5,3)
            cf = st.number_input("Caffeine",0,10,1)
            st_time = st.slider("Screen Time",0,12,4)

            if st.form_submit_button("Save Data"):

                new_row = pd.DataFrame({
                    "date":[d],
                    "sleep_hours":[sh],
                    "mood":[md],
                    "productivity":[pr],
                    "caffeine":[cf],
                    "screen_time":[st_time]
                })

                df_new = pd.concat([df,new_row], ignore_index=True)

                df_new.to_csv("data.csv", index=False)

                st.success("Data saved successfully!")