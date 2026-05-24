from __future__ import annotations

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots


st.set_page_config(page_title="Earned Value Analysis", page_icon="📊", layout="centered")


def build_evm_chart(
    pv: float,
    ac: float,
    ev: float,
    eac: float,
    etc: float,
    cpi: float,
    spi: float,
    tcpi: float,
) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    money_labels = ["PV", "AC", "EV", "EAC", "ETC"]
    money_values = [pv, ac, ev, eac, etc]

    index_labels = ["CPI", "SPI", "TCPI"]
    index_values = [cpi, spi, tcpi]

    fig.add_trace(
        go.Bar(
            x=money_labels,
            y=money_values,
            name="Value ($)",
            marker_color="#1f77b4",
            text=[f"{value:,.2f}" for value in money_values],
            textposition="outside",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=index_labels,
            y=index_values,
            name="Performance Index",
            mode="lines+markers+text",
            line=dict(color="#d62728", width=3),
            marker=dict(size=10),
            text=[f"{value:.2f}" for value in index_values],
            textposition="top center",
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title="EVM Metrics Overview",
        template="plotly_white",
        height=520,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=30, r=30, t=70, b=30),
    )
    fig.update_yaxes(title_text="Monetary Value ($)", secondary_y=False)
    fig.update_yaxes(title_text="Performance Index", secondary_y=True)
    return fig


st.title("📊 Earned Value Analysis Tool")
st.markdown(
    "Enter your project values below to get an instant health check, advanced forecast metrics, and a chart."
)

st.divider()

col1, col2 = st.columns(2)
with col1:
    bac = st.number_input("Budget at Completion (BAC) $", min_value=0.0, format="%.2f")
    pv = st.number_input("Planned Value (PV) $", min_value=0.0, format="%.2f")
with col2:
    ac = st.number_input("Actual Cost (AC) $", min_value=0.0, format="%.2f")
    ev = st.number_input("Earned Value (EV) $", min_value=0.0, format="%.2f")

st.divider()

if st.button("🔍 Analyse Project", use_container_width=True):
    if ac == 0 or pv == 0 or bac == 0:
        st.error("⚠️ BAC, PV, and AC cannot be zero.")
    else:
        cv = ev - ac
        sv = ev - pv
        cpi = ev / ac
        spi = ev / pv

        eac = bac / cpi if cpi != 0 else 0.0
        etc = eac - ac
        tcpi = (bac - ev) / (bac - ac) if bac - ac != 0 else 0.0

        st.subheader("📈 Core Results")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Cost Variance (CV)", f"${cv:,.2f}")
        m2.metric("Schedule Variance (SV)", f"${sv:,.2f}")
        m3.metric("CPI", f"{cpi:.2f}")
        m4.metric("SPI", f"{spi:.2f}")

        st.subheader("📌 Forecast Metrics")
        f1, f2, f3 = st.columns(3)
        f1.metric("Estimate at Completion (EAC)", f"${eac:,.2f}")
        f2.metric("Estimate to Complete (ETC)", f"${etc:,.2f}")
        f3.metric("To Complete Performance Index (TCPI)", f"{tcpi:.2f}")

        st.divider()
        st.subheader("🩺 Project Health")

        if cv == 0:
            st.success("✅ Cost: Project is exactly on budget")
        elif cv > 0:
            st.success("✅ Cost: Project is under budget")
        else:
            st.error("❌ Cost: Project is over budget")

        if sv == 0:
            st.success("✅ Schedule: Project is exactly on schedule")
        elif sv > 0:
            st.success("✅ Schedule: Project is ahead of schedule")
        else:
            st.error("❌ Schedule: Project is behind schedule")

        if cpi == 1:
            st.info("ℹ️ CPI: Cost efficiency is perfect (1.0)")
        elif cpi > 1:
            st.success(f"✅ CPI {cpi:.2f}: Getting more value than spent")
        else:
            st.warning(f"⚠️ CPI {cpi:.2f}: Spending more than planned")

        if spi == 1:
            st.info("ℹ️ SPI: Schedule efficiency is perfect (1.0)")
        elif spi > 1:
            st.success(f"✅ SPI {spi:.2f}: Ahead of schedule")
        else:
            st.warning(f"⚠️ SPI {spi:.2f}: Behind schedule")

        if tcpi == 0:
            st.info("ℹ️ TCPI could not be calculated because BAC equals AC.")
        elif tcpi <= 1:
            st.success(
                f"✅ TCPI {tcpi:.2f}: Remaining performance target looks achievable"
            )
        else:
            st.warning(
                f"⚠️ TCPI {tcpi:.2f}: Remaining work needs higher-than-current efficiency"
            )

        st.divider()
        st.subheader("📉 EVM Graph")
        chart = build_evm_chart(pv, ac, ev, eac, etc, cpi, spi, tcpi)
        st.plotly_chart(chart, use_container_width=True)

        st.subheader("📋 Summary Table")
        st.dataframe(
            {
                "Metric": [
                    "BAC",
                    "PV",
                    "AC",
                    "EV",
                    "CV",
                    "SV",
                    "CPI",
                    "SPI",
                    "EAC",
                    "ETC",
                    "TCPI",
                ],
                "Value": [
                    f"{bac:,.2f}",
                    f"{pv:,.2f}",
                    f"{ac:,.2f}",
                    f"{ev:,.2f}",
                    f"{cv:,.2f}",
                    f"{sv:,.2f}",
                    f"{cpi:.2f}",
                    f"{spi:.2f}",
                    f"{eac:,.2f}",
                    f"{etc:,.2f}",
                    f"{tcpi:.2f}",
                ],
            },
            use_container_width=True,
            hide_index=True,
        )

st.divider()
st.caption("Built with Python & Streamlit · Earned Value Analysis Tool")
