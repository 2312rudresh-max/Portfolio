import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nifty 50 DCF Valuation",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Inter:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main { background-color: #0d0d0d; color: #e8e8e8; }

    h1, h2, h3 { font-family: 'IBM Plex Mono', monospace; }

    .hero-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 2.4rem;
        font-weight: 600;
        color: #f0f0f0;
        letter-spacing: -0.02em;
        line-height: 1.2;
        margin-bottom: 0.2rem;
    }

    .hero-sub {
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        color: #888;
        font-weight: 300;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 2rem;
    }

    .metric-card {
        background: #161616;
        border: 1px solid #2a2a2a;
        border-radius: 4px;
        padding: 1.2rem 1.4rem;
    }

    .metric-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.3rem;
    }

    .metric-value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 1.8rem;
        font-weight: 600;
        color: #f0f0f0;
    }

    .metric-value.up { color: #00c896; }
    .metric-value.down { color: #ff4d4d; }

    .section-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem;
        color: #444;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        border-bottom: 1px solid #1f1f1f;
        padding-bottom: 0.4rem;
        margin-bottom: 1rem;
    }

    .assumption-table {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.8rem;
    }

    .verdict-banner {
        padding: 1rem 1.5rem;
        border-radius: 4px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 1rem;
        font-weight: 600;
        margin-top: 1rem;
    }

    .verdict-buy {
        background: #0a2e1f;
        border: 1px solid #00c896;
        color: #00c896;
    }

    .verdict-sell {
        background: #2e0a0a;
        border: 1px solid #ff4d4d;
        color: #ff4d4d;
    }

    .verdict-hold {
        background: #1f1a08;
        border: 1px solid #f0b429;
        color: #f0b429;
    }

    .data-note {
        font-size: 0.75rem;
        color: #555;
        font-style: italic;
        margin-top: 0.3rem;
    }

    div[data-testid="stSidebar"] {
        background-color: #111111;
    }

    .stSlider > div > div { background: #222; }

    footer { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Nifty 50 tickers ─────────────────────────────────────────────────────────
NIFTY50 = {
    "Reliance Industries":      "RELIANCE.NS",
    "TCS":                      "TCS.NS",
    "HDFC Bank":                "HDFCBANK.NS",
    "Infosys":                  "INFY.NS",
    "ICICI Bank":               "ICICIBANK.NS",
    "Hindustan Unilever":       "HINDUNILVR.NS",
    "ITC":                      "ITC.NS",
    "Kotak Mahindra Bank":      "KOTAKBANK.NS",
    "L&T":                      "LT.NS",
    "Axis Bank":                "AXISBANK.NS",
    "Sun Pharma":               "SUNPHARMA.NS",
    "Maruti Suzuki":            "MARUTI.NS",
    "Bajaj Finance":            "BAJFINANCE.NS",
    "Bharti Airtel":            "BHARTIARTL.NS",
    "Asian Paints":             "ASIANPAINT.NS",
    "HCL Technologies":         "HCLTECH.NS",
    "Wipro":                    "WIPRO.NS",
    "UltraTech Cement":         "ULTRACEMCO.NS",
    "Titan Company":            "TITAN.NS",
    "Nestle India":             "NESTLEIND.NS",
    "NTPC":                     "NTPC.NS",
    "Power Grid":               "POWERGRID.NS",
    "Tech Mahindra":            "TECHM.NS",
    "JSW Steel":                "JSWSTEEL.NS",
    "Tata Motors":              "TATAMOTORS.NS",
    "Tata Steel":               "TATASTEEL.NS",
    "Bajaj Auto":               "BAJAJ-AUTO.NS",
    "Eicher Motors":            "EICHERMOT.NS",
    "Hero MotoCorp":            "HEROMOTOCO.NS",
    "Divis Laboratories":       "DIVISLAB.NS",
    "Dr. Reddy's":              "DRREDDY.NS",
    "Cipla":                    "CIPLA.NS",
    "BPCL":                     "BPCL.NS",
    "ONGC":                     "ONGC.NS",
    "Coal India":               "COALINDIA.NS",
    "Grasim Industries":        "GRASIM.NS",
    "Shree Cement":             "SHREECEM.NS",
    "Hindalco":                 "HINDALCO.NS",
    "Tata Consumer Products":   "TATACONSUM.NS",
    "Adani Ports":              "ADANIPORTS.NS",
    "Adani Enterprises":        "ADANIENT.NS",
    "Apollo Hospitals":         "APOLLOHOSP.NS",
    "Dmart (Avenue Supermarts)":"DMART.NS",
    "SBI Life Insurance":       "SBILIFE.NS",
    "HDFC Life Insurance":      "HDFCLIFE.NS",
    "Bajaj Finserv":            "BAJAJFINSV.NS",
    "IndusInd Bank":            "INDUSINDBK.NS",
    "SBI":                      "SBIN.NS",
    "M&M":                      "M&M.NS",
    "Tata Consultancy Services":"TCS.NS",
}

# ── Helper functions ──────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_financials(ticker: str):
    stock = yf.Ticker(ticker)
    info = stock.info
    cf = stock.cashflow
    income = stock.income_stmt
    balance = stock.balance_sheet
    return info, cf, income, balance


def safe_get(df, keys, default=None):
    """Try multiple row keys on a DataFrame, return first match."""
    if df is None or df.empty:
        return default
    for key in keys:
        if key in df.index:
            row = df.loc[key].dropna()
            if not row.empty:
                return float(row.iloc[0])
    return default


def run_dcf(
    fcff_base: float,
    revenue_growth: list,
    ebit_margin: float,
    tax_rate: float,
    da_pct: float,
    capex_pct: float,
    wc_pct: float,
    wacc: float,
    terminal_growth: float,
    net_debt: float,
    shares_outstanding: float,
    revenue_base: float,
):
    """5-year DCF → equity value per share (all monetary inputs in ₹ Cr)."""
    fcffs = []
    rev = revenue_base
    for g in revenue_growth:
        rev *= (1 + g)
        ebit = rev * ebit_margin
        nopat = ebit * (1 - tax_rate)
        da = rev * da_pct
        capex = rev * capex_pct
        delta_wc = rev * wc_pct
        fcff = nopat + da - capex - delta_wc
        fcffs.append(fcff)

    # Terminal value
    terminal_fcff = fcffs[-1] * (1 + terminal_growth)
    tv = terminal_fcff / (wacc - terminal_growth)

    # Discount
    pv_fcffs = sum(f / (1 + wacc) ** (i + 1) for i, f in enumerate(fcffs))
    pv_tv = tv / (1 + wacc) ** len(fcffs)

    enterprise_value = pv_fcffs + pv_tv
    equity_value = enterprise_value - net_debt
    value_per_share = (equity_value * 1e7) / shares_outstanding  # Cr → ₹

    return {
        "fcffs": fcffs,
        "pv_fcffs": pv_fcffs,
        "pv_tv": pv_tv,
        "enterprise_value": enterprise_value,
        "equity_value": equity_value,
        "value_per_share": value_per_share,
        "terminal_value": tv,
    }


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-label">Select Company</div>', unsafe_allow_html=True)
    company_name = st.selectbox("", list(NIFTY50.keys()), label_visibility="collapsed")
    ticker = NIFTY50[company_name]

    st.markdown('<div class="section-label" style="margin-top:1.5rem">DCF Assumptions</div>', unsafe_allow_html=True)

    rev_g1 = st.slider("Revenue Growth — Yr 1 (%)", 0, 40, 12) / 100
    rev_g2 = st.slider("Revenue Growth — Yr 2 (%)", 0, 40, 11) / 100
    rev_g3 = st.slider("Revenue Growth — Yr 3 (%)", 0, 40, 10) / 100
    rev_g4 = st.slider("Revenue Growth — Yr 4 (%)", 0, 35, 9) / 100
    rev_g5 = st.slider("Revenue Growth — Yr 5 (%)", 0, 35, 8) / 100

    st.markdown("---")
    ebit_margin = st.slider("EBIT Margin (%)", 1, 50, 15) / 100
    tax_rate    = st.slider("Effective Tax Rate (%)", 10, 40, 25) / 100
    da_pct      = st.slider("D&A as % of Revenue (%)", 1, 15, 4) / 100
    capex_pct   = st.slider("Capex as % of Revenue (%)", 1, 20, 6) / 100
    wc_pct      = st.slider("Δ Working Capital as % of Revenue (%)", 0, 10, 2) / 100

    st.markdown("---")
    wacc            = st.slider("WACC (%)", 6, 20, 11) / 100
    terminal_growth = st.slider("Terminal Growth Rate (%)", 2, 8, 4) / 100

# ── Main ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">Nifty 50 DCF Valuation</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Intrinsic value · Live market data · 5-year FCFF model</div>', unsafe_allow_html=True)

with st.spinner(f"Fetching {company_name} financials..."):
    try:
        info, cf, income, balance = fetch_financials(ticker)
        fetch_ok = True
    except Exception as e:
        st.error(f"Could not fetch data for {ticker}: {e}")
        fetch_ok = False

if fetch_ok:
    # ── Extract financials ────────────────────────────────────────────────────
    current_price    = info.get("currentPrice") or info.get("regularMarketPrice") or 0
    shares           = info.get("sharesOutstanding") or 1
    market_cap_cr    = (current_price * shares) / 1e7  # ₹ Cr

    revenue_base_cr = safe_get(
        income,
        ["Total Revenue", "Revenue", "Net Revenue"],
        default=market_cap_cr * 0.5
    ) / 1e7  # yfinance returns in ₹ units; convert to Cr

    total_debt_cr = safe_get(
        balance,
        ["Total Debt", "Long Term Debt", "Short Long Term Debt"],
        default=0
    ) / 1e7

    cash_cr = safe_get(
        balance,
        ["Cash And Cash Equivalents", "Cash", "Cash Cash Equivalents And Short Term Investments"],
        default=0
    ) / 1e7

    net_debt_cr = total_debt_cr - cash_cr

    # ── Run DCF ───────────────────────────────────────────────────────────────
    result = run_dcf(
        fcff_base=0,
        revenue_growth=[rev_g1, rev_g2, rev_g3, rev_g4, rev_g5],
        ebit_margin=ebit_margin,
        tax_rate=tax_rate,
        da_pct=da_pct,
        capex_pct=capex_pct,
        wc_pct=wc_pct,
        wacc=wacc,
        terminal_growth=terminal_growth,
        net_debt=net_debt_cr,
        shares_outstanding=shares,
        revenue_base=revenue_base_cr,
    )

    intrinsic = result["value_per_share"]
    upside    = ((intrinsic - current_price) / current_price) * 100 if current_price else 0

    # ── Verdict ───────────────────────────────────────────────────────────────
    if upside > 15:
        verdict_class = "verdict-buy"
        verdict_text  = f"▲ UNDERVALUED — {upside:+.1f}% upside to intrinsic value"
    elif upside < -15:
        verdict_class = "verdict-sell"
        verdict_text  = f"▼ OVERVALUED — {upside:+.1f}% downside to intrinsic value"
    else:
        verdict_class = "verdict-hold"
        verdict_text  = f"◆ FAIRLY VALUED — {upside:+.1f}% to intrinsic value"

    # ── Top metrics row ───────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Current Price</div>
            <div class="metric-value">₹{current_price:,.0f}</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        color_class = "up" if upside > 0 else "down"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Intrinsic Value (DCF)</div>
            <div class="metric-value {color_class}">₹{intrinsic:,.0f}</div>
        </div>""", unsafe_allow_html=True)

    with col3:
        color_class = "up" if upside > 0 else "down"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Upside / Downside</div>
            <div class="metric-value {color_class}">{upside:+.1f}%</div>
        </div>""", unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Market Cap</div>
            <div class="metric-value">₹{market_cap_cr:,.0f} Cr</div>
        </div>""", unsafe_allow_html=True)

    # ── Verdict banner ────────────────────────────────────────────────────────
    st.markdown(f'<div class="verdict-banner {verdict_class}">{verdict_text}</div>',
                unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Two-column detail ─────────────────────────────────────────────────────
    left, right = st.columns([1.1, 1])

    with left:
        st.markdown('<div class="section-label">Projected Free Cash Flows (₹ Cr)</div>', unsafe_allow_html=True)

        fcff_data = pd.DataFrame({
            "Year": [f"Year {i+1}" for i in range(5)],
            "FCFF (₹ Cr)": [f"₹{v:,.0f}" for v in result["fcffs"]],
        })
        st.dataframe(fcff_data, hide_index=True, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Value Bridge (₹ Cr)</div>', unsafe_allow_html=True)

        bridge_data = pd.DataFrame({
            "Component": [
                "PV of FCFFs",
                "PV of Terminal Value",
                "Enterprise Value",
                "Less: Net Debt",
                "Equity Value",
            ],
            "₹ Cr": [
                f"₹{result['pv_fcffs']:,.0f}",
                f"₹{result['pv_tv']:,.0f}",
                f"₹{result['enterprise_value']:,.0f}",
                f"(₹{result['equity_value'] - (result['enterprise_value'] - net_debt_cr):,.0f})" if net_debt_cr > 0 else "₹0",
                f"₹{result['equity_value']:,.0f}",
            ],
        })
        st.dataframe(bridge_data, hide_index=True, use_container_width=True)

    with right:
        st.markdown('<div class="section-label">Key Assumptions</div>', unsafe_allow_html=True)

        assump_data = pd.DataFrame({
            "Parameter": [
                "Revenue Base",
                "Growth Yr 1–5",
                "EBIT Margin",
                "Tax Rate",
                "D&A % Revenue",
                "Capex % Revenue",
                "WACC",
                "Terminal Growth",
                "Net Debt",
            ],
            "Value": [
                f"₹{revenue_base_cr:,.0f} Cr",
                f"{rev_g1*100:.0f} / {rev_g2*100:.0f} / {rev_g3*100:.0f} / {rev_g4*100:.0f} / {rev_g5*100:.0f}%",
                f"{ebit_margin*100:.1f}%",
                f"{tax_rate*100:.1f}%",
                f"{da_pct*100:.1f}%",
                f"{capex_pct*100:.1f}%",
                f"{wacc*100:.1f}%",
                f"{terminal_growth*100:.1f}%",
                f"₹{net_debt_cr:,.0f} Cr",
            ],
        })
        st.dataframe(assump_data, hide_index=True, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Company Data (Live)</div>', unsafe_allow_html=True)

        pe   = info.get("trailingPE", "N/A")
        pb   = info.get("priceToBook", "N/A")
        roe  = info.get("returnOnEquity", None)
        roe_str = f"{roe*100:.1f}%" if roe else "N/A"
        sector = info.get("sector", "N/A")

        live_data = pd.DataFrame({
            "Metric": ["Sector", "Trailing P/E", "P/B", "ROE"],
            "Value":  [sector,
                       f"{pe:.1f}x" if isinstance(pe, float) else pe,
                       f"{pb:.2f}x" if isinstance(pb, float) else pb,
                       roe_str],
        })
        st.dataframe(live_data, hide_index=True, use_container_width=True)

    # ── Sensitivity table ─────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Sensitivity — Intrinsic Value per Share (₹) | WACC vs Terminal Growth</div>',
                unsafe_allow_html=True)

    wacc_range = [wacc - 0.02, wacc - 0.01, wacc, wacc + 0.01, wacc + 0.02]
    tgr_range  = [terminal_growth - 0.01, terminal_growth, terminal_growth + 0.01, terminal_growth + 0.02]

    rows = []
    for w in wacc_range:
        row = {}
        for tg in tgr_range:
            if w <= tg:
                row[f"TGR {tg*100:.1f}%"] = "N/A"
                continue
            r = run_dcf(
                fcff_base=0,
                revenue_growth=[rev_g1, rev_g2, rev_g3, rev_g4, rev_g5],
                ebit_margin=ebit_margin,
                tax_rate=tax_rate,
                da_pct=da_pct,
                capex_pct=capex_pct,
                wc_pct=wc_pct,
                wacc=w,
                terminal_growth=tg,
                net_debt=net_debt_cr,
                shares_outstanding=shares,
                revenue_base=revenue_base_cr,
            )
            row[f"TGR {tg*100:.1f}%"] = f"₹{r['value_per_share']:,.0f}"
        rows.append(row)

    sens_df = pd.DataFrame(rows, index=[f"WACC {w*100:.1f}%" for w in wacc_range])
    st.dataframe(sens_df, use_container_width=True)

    st.markdown(
        '<p class="data-note">Data sourced from Yahoo Finance via yfinance. '
        'Revenue base and balance sheet items pulled from latest available annual filing. '
        'This model is for illustrative purposes only and does not constitute investment advice.</p>',
        unsafe_allow_html=True
    )
