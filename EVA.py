from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(page_title="Earned Value Analysis", page_icon="chart_with_downwards_trend", layout="wide")


def sample_evm_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "period": [
                "2026-01-31",
                "2026-02-28",
                "2026-03-31",
                "2026-04-30",
                "2026-05-31",
                "2026-06-30",
            ],
            "pv": [10000, 22000, 36000, 50000, 62000, 75000],
            "ev": [8000, 20000, 31000, 45000, 60000, 65000],
            "ac": [9000, 21000, 34000, 48000, 64000, 70000],
        }
    )


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    working = df.copy()
    working.columns = [str(column).strip().lower() for column in working.columns]

    required = ["period", "pv", "ev", "ac"]
    missing = [column for column in required if column not in working.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))

    working["period"] = pd.to_datetime(working["period"], errors="coerce")
    for column in ["pv", "ev", "ac"]:
        working[column] = pd.to_numeric(working[column], errors="coerce")

    working = working.dropna(subset=["period", "pv", "ev", "ac"]).sort_values("period")
    if working.empty:
        raise ValueError("No valid data available after cleaning. Check your dates and numeric values.")

    working["cv"] = working["ev"] - working["ac"]
    working["sv"] = working["ev"] - working["pv"]
    working["cpi"] = working.apply(lambda row: row["ev"] / row["ac"] if row["ac"] else 0.0, axis=1)
    working["spi"] = working.apply(lambda row: row["ev"] / row["pv"] if row["pv"] else 0.0, axis=1)

    return working


def build_s_curve(df: pd.DataFrame) -> go.Figure:
    latest = df.iloc[-1]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["period"],
            y=df["pv"],
            mode="lines+markers",
            name="Planned Value (PV)",
            line=dict(color="#17becf", width=3, dash="dash"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["period"],
            y=df["ev"],
            mode="lines+markers",
            name="Earned Value (EV)",
            line=dict(color="#1f77b4", width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["period"],
            y=df["ac"],
            mode="lines+markers",
            name="Actual Cost (AC)",
            line=dict(color="#f2c14e", width=3, dash="longdash"),
        )
    )

    fig.add_vline(x=latest["period"], line_width=2, line_dash="dot", line_color="#8c8c8c")
    fig.add_annotation(
        x=latest["period"],
        y=max(latest["pv"], latest["ev"], latest["ac"]),
        text="Time now",
        showarrow=False,
        yshift=18,
        font=dict(color="#4a4a4a"),
    )

    fig.add_shape(
        type="line",
        x0=latest["period"],
        x1=latest["period"],
        y0=latest["ev"],
        y1=latest["pv"],
        line=dict(color="#17becf", width=2, dash="dot"),
    )
    fig.add_annotation(
        x=latest["period"],
        y=(latest["ev"] + latest["pv"]) / 2,
        text=f"SV: {latest['sv']:,.2f}",
        showarrow=False,
        xshift=-55,
        bgcolor="rgba(23, 190, 207, 0.12)",
    )

    fig.add_shape(
        type="line",
        x0=latest["period"],
        x1=latest["period"],
        y0=latest["ev"],
        y1=latest["ac"],
        line=dict(color="#f2c14e", width=2, dash="dot"),
    )
    fig.add_annotation(
        x=latest["period"],
        y=(latest["ev"] + latest["ac"]) / 2,
        text=f"CV: {latest['cv']:,.2f}",
        showarrow=False,
        xshift=55,
        bgcolor="rgba(242, 193, 78, 0.15)",
    )

    fig.update_layout(
        title="Earned Value Management S-Curve",
        template="plotly_white",
        height=620,
        hovermode="x unified",
        xaxis_title="Time",
        yaxis_title="Cost / Value",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=70, b=40),
    )
    fig.update_yaxes(tickformat=",.0f")
    return fig


def status_text(label: str, value: float, positive_message: str, negative_message: str) -> None:
    if value > 0:
        st.success(f"{label}: {positive_message}")
    elif value < 0:
        st.error(f"{label}: {negative_message}")
    else:
        st.info(f"{label}: Exactly on target")


st.title("Earned Value Analysis Tool")
st.markdown(
    "Use time-phased project data to plot a real EVM curve with Planned Value, Earned Value, Actual Cost, and visible variance analysis."
)

st.subheader("1. Input Your Backend Data")
st.caption("Edit the table directly or replace it later with Excel upload. Required columns: period, pv, ev, ac")

raw_data = st.data_editor(
    sample_evm_data(),
    num_rows="dynamic",
    use_container_width=True,
    key="evm_data_editor",
)

if st.button("Analyse Project", use_container_width=True):
    try:
        evm_data = prepare_data(pd.DataFrame(raw_data))
        latest = evm_data.iloc[-1]

        st.subheader("2. Latest Period KPIs")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("PV", f"{latest['pv']:,.2f}")
        k2.metric("EV", f"{latest['ev']:,.2f}")
        k3.metric("AC", f"{latest['ac']:,.2f}")
        k4.metric("CV", f"{latest['cv']:,.2f}")

        k5, k6, k7, k8 = st.columns(4)
        k5.metric("SV", f"{latest['sv']:,.2f}")
        k6.metric("CPI", f"{latest['cpi']:.2f}")
        k7.metric("SPI", f"{latest['spi']:.2f}")
        k8.metric("Status Date", latest["period"].strftime("%d-%b-%Y"))

        st.subheader("3. EVM S-Curve")
        st.plotly_chart(build_s_curve(evm_data), use_container_width=True)

        st.subheader("4. Variance Analysis")
        a1, a2 = st.columns(2)
        with a1:
            status_text(
                "Cost Variance",
                latest["cv"],
                "Project is under budget at the latest status date",
                "Project is over budget at the latest status date",
            )
            if latest["cpi"] > 1:
                st.success(f"CPI: {latest['cpi']:.2f} means cost efficiency is favorable")
            elif latest["cpi"] < 1:
                st.warning(f"CPI: {latest['cpi']:.2f} means cost efficiency is unfavorable")
            else:
                st.info("CPI: 1.00 means cost performance is exactly on target")
        with a2:
            status_text(
                "Schedule Variance",
                latest["sv"],
                "Project is ahead of schedule at the latest status date",
                "Project is behind schedule at the latest status date",
            )
            if latest["spi"] > 1:
                st.success(f"SPI: {latest['spi']:.2f} means schedule efficiency is favorable")
            elif latest["spi"] < 1:
                st.warning(f"SPI: {latest['spi']:.2f} means schedule efficiency is unfavorable")
            else:
                st.info("SPI: 1.00 means schedule performance is exactly on target")

        st.subheader("5. Time-Phased Data Table")
        display = evm_data.copy()
        display["period"] = display["period"].dt.strftime("%Y-%m-%d")
        st.dataframe(display, use_container_width=True, hide_index=True)

    except ValueError as error:
        st.error(str(error))

st.divider()
st.caption("Built with Python and Streamlit for proper project controls style earned value analysis.")
