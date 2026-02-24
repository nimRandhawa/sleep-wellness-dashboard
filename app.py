import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def load_data():
    df = pd.read_csv("data.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date")

st.set_page_config(page_title="Sleep & Wellness Dashboard", layout="wide")
st.title("Sleep & Wellness Analytics Dashboard")

st.subheader("Log Today’s Data")

with st.form("daily_log", clear_on_submit=True):
    date = st.date_input("Date")
    sleep_hours = st.slider("Sleep Hours", 0, 12, 7)
    mood = st.slider("Mood (1 = low, 5 = great)", 1, 5, 3)
    productivity = st.slider("Productivity (1 = low, 5 = high)", 1, 5, 3)
    caffeine = st.number_input("Cups of Caffeine", 0, 10, 0)
    screen_time = st.slider("Screen Time (hours)", 0, 12, 4)

    submitted = st.form_submit_button("Add Entry")

if submitted:
    new_row = pd.DataFrame([{
        "date": date,
        "sleep_hours": sleep_hours,
        "mood": mood,
        "productivity": productivity,
        "caffeine": caffeine,
        "screen_time": screen_time
    }])

    existing_dates = set(df["date"].dt.date)

    if date in existing_dates:
        st.error("An entry for this date already exists. Choose a different date.")
    else:
        df_out = pd.concat([df, new_row], ignore_index=True)
        df_out.to_csv("data.csv", index=False)
        st.success("Entry added!")
        df = load_data()

df = load_data()

existing_dates = set(df["date"].dt.date)

st.subheader("Quick Insights")
avg_sleep = df["sleep_hours"].mean()
avg_prod = df["productivity"].mean()

st.write(f"Average sleep: **{avg_sleep:.1f} hours/night**")
st.write(f"Average productivity: **{avg_prod:.1f} / 5**")

low_sleep_days = df[df["sleep_hours"] < 6]
if len(low_sleep_days) >= 2:
    st.write(f"On days with < 6 hours sleep, average productivity was **{low_sleep_days['productivity'].mean():.1f} / 5**.")
st.subheader("Sleep vs Productivity Over Time")

fig, ax = plt.subplots()
ax.plot(df["date"], df["sleep_hours"], marker="o", label="Sleep Hours")
ax.plot(df["date"], df["productivity"], marker="o", label="Productivity")
ax.set_xlabel("Date")
ax.set_ylabel("Value")
ax.legend()
st.pyplot(fig)

st.subheader("Raw Data")
st.dataframe(df)
