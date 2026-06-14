import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nifty 50 Valuation Suite",
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

    .model-note {
        font-size: 0.8rem;
        color: #999;
        background: #161616;
        border-left: 3px solid #00c896;
        padding: 0.6rem 1rem;
        margin-bottom: 1.2rem;
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


def verdict(upside):
    if upside > 15:
        return "verdict-buy", f"▲ UNDERVALUED — {upside:+.1f}% upside to intrinsic value"
    elif upside < -15:
        return "verdict-sell", f"▼ OVERVALUED — {upside:+.1f}% downside to intrinsic value"
    else:
        return "verdict-hold", f"◆ FAIRLY VALUED — {upside:+.1f}% to intrinsic value"


def metric_card(label, value, color_class=""):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value {color_class}">{value}</div>
    </div>""", unsafe_allow_html=True)


# ── DCF (FCFF) engine ───────────────────────────────────────────────────────
def run_fcff_dcf(revenue_base, revenue_growth, ebit_margin, tax_rate, da_pct,
                  capex_pct, wc_pct, wacc, terminal_growth, net_debt, shares):
    fcffs = []
    rev = revenue_base
    for g in revenue_growth:
        rev *= (1 + g)
        ebit = rev * ebit_margin
        nopat = ebit * (1 - tax_rate)
        da = rev * da_pct
        capex = rev * capex_pct
        delta_wc = rev * wc_pct
        fcffs.append(nopat + da - capex - delta_wc)

    terminal_fcff = fcffs[-1] * (1 + terminal_growth)
    tv = terminal_fcff / (wacc - terminal_growth)

    pv_fcffs = sum(f / (1 + wacc) ** (i + 1) for i, f in enumerate(fcffs))
    pv_tv = tv / (1 + wacc) ** len(fcffs)

    enterprise_value = pv_fcffs + pv_tv
    equity_value = enterprise_value - net_debt
    value_per_share = (equity_value * 1e7) / shares

    return {
        "fcffs": fcffs, "pv_fcffs": pv_fcffs, "pv_tv": pv_tv,
        "enterprise_value": enterprise_value, "equity_value": equity_value,
        "value_per_share": value_per_share, "terminal_value": tv,
    }


# ── FCFE engine ───────────────────────────────────────────────────────────────
def run_fcfe(revenue_base, revenue_growth, net_margin, da_pct, capex_pct,
              wc_pct, net_borrowing_pct, ke, terminal_growth, shares):
    fcfes = []
    rev = revenue_base
    for g in revenue_growth:
        rev *= (1 + g)
        net_income = rev * net_margin
        da = rev * da_pct
        capex = rev * capex_pct
        delta_wc = rev * wc_pct
        net_borrowing = rev * net_borrowing_pct
        fcfes.append(net_income + da - capex - delta_wc + net_borrowing)

    terminal_fcfe = fcfes[-1] * (1 + terminal_growth)
    tv = terminal_fcfe / (ke - terminal_growth)

    pv_fcfes = sum(f / (1 + ke) ** (i + 1) for i, f in enumerate(fcfes))
    pv_tv = tv / (1 + ke) ** len(fcfes)

    equity_value = pv_fcfes + pv_tv
    value_per_share = (equity_value * 1e7) / shares

    return {
        "fcfes": fcfes, "pv_fcfes": pv_fcfes, "pv_tv": pv_tv,
        "equity_value": equity_value, "value_per_share": value_per_share,
        "terminal_value": tv,
    }


# ── DDM engine (two-stage Gordon Growth) ───────────────────────────────────────
def run_ddm(dps0, growth_stage1, years_stage1, terminal_growth, ke):
    divs = []
    d = dps0
    for _ in range(years_stage1):
        d *= (1 + growth_stage1)
        divs.append(d)

    pv_divs = sum(dv / (1 + ke) ** (i + 1) for i, dv in enumerate(divs))

    terminal_div = divs[-1] * (1 + terminal_growth)
    tv = terminal_div / (ke - terminal_growth)
    pv_tv = tv / (1 + ke) ** years_stage1

    value_per_share = pv_divs + pv_tv
    return {
        "divs": divs, "pv_divs": pv_divs, "pv_tv": pv_tv,
        "value_per_share": value_per_share, "terminal_value": tv,
    }


# ── Residual Income Model engine ────────────────────────────────────────────────
def run_rim(bvps0, roe, ke, book_growth, terminal_growth, years=5):
    bvps = bvps0
    ris = []
    bvs = []
    for _ in range(years):
        ri = (roe - ke) * bvps
        ris.append(ri)
        bvs.append(bvps)
        bvps *= (1 + book_growth)

    pv_ris = sum(ri / (1 + ke) ** (i + 1) for i, ri in enumerate(ris))

    terminal_ri = ris[-1] * (1 + terminal_growth)
    tv = terminal_ri / (ke - terminal_growth)
    pv_tv = tv / (1 + ke) ** years

    value_per_share = bvps0 + pv_ris + pv_tv
    return {
        "ris": ris, "bvs": bvs, "pv_ris": pv_ris, "pv_tv": pv_tv,
        "value_per_share": value_per_share, "terminal_value": tv,
    }


# ── Sidebar: company + market assumptions ───────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-label">Select Company</div>', unsafe_allow_html=True)
    company_name = st.selectbox("", list(NIFTY50.keys()), label_visibility="collapsed")
    ticker = NIFTY50[company_name]

    st.markdown('<div class="section-label" style="margin-top:1.5rem">Market Assumptions (CAPM)</div>', unsafe_allow_html=True)
    risk_free = st.slider("Risk-Free Rate (%) — 10Y G-Sec", 4.0, 9.0, 7.0, 0.1) / 100
    erp = st.slider("Equity Risk Premium (%)", 3.0, 9.0, 5.5, 0.1) / 100

# ── Main ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">Nifty 50 Valuation Suite</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Intrinsic value · Live market data · FCFF · FCFE · DDM · Residual Income</div>', unsafe_allow_html=True)

with st.spinner(f"Fetching {company_name} financials..."):
    try:
        info, cf, income, balance = fetch_financials(ticker)
        fetch_ok = True
    except Exception as e:
        st.error(f"Could not fetch data for {ticker}: {e}")
        fetch_ok = False

if fetch_ok:
    # ── Shared extracted financials ──────────────────────────────────────────
    current_price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
    shares = info.get("sharesOutstanding") or 1
    market_cap_cr = (current_price * shares) / 1e7
    beta = info.get("beta") or 1.0

    # cost of equity via CAPM
    ke = risk_free + beta * erp

    revenue_base_cr = safe_get(
        income, ["Total Revenue", "Revenue", "Net Revenue"],
        default=market_cap_cr * 0.5
    ) / 1e7

    total_debt_cr = safe_get(
        balance, ["Total Debt", "Long Term Debt", "Short Long Term Debt"], default=0
    ) / 1e7

    cash_cr = safe_get(
        balance, ["Cash And Cash Equivalents", "Cash",
                  "Cash Cash Equivalents And Short Term Investments"], default=0
    ) / 1e7

    net_debt_cr = total_debt_cr - cash_cr

    bvps0 = info.get("bookValue") or 0
    dps0 = info.get("dividendRate") or 0
    current_roe = info.get("returnOnEquity") or 0.0

    # ── Top metric row ────────────────────────────────────────────────────────
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        metric_card("Current Price", f"₹{current_price:,.0f}")
    with col2:
        metric_card("Market Cap", f"₹{market_cap_cr:,.0f} Cr")
    with col3:
        metric_card("Beta", f"{beta:.2f}")
    with col4:
        metric_card("Cost of Equity (CAPM)", f"{ke*100:.1f}%")
    with col5:
        sector = info.get("sector", "N/A")
        metric_card("Sector", sector)

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["FCFF · DCF", "FCFE", "DDM", "Residual Income"])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — FCFF DCF
    # ══════════════════════════════════════════════════════════════════════════
    with tab1:
        st.markdown(
            '<div class="model-note">Free Cash Flow to Firm, discounted at WACC. '
            'Best suited to non-financial companies where capex and working capital '
            'are meaningful drivers.</div>', unsafe_allow_html=True)

        left, right = st.columns([1, 1.4])
        with left:
            st.markdown('<div class="section-label">Assumptions</div>', unsafe_allow_html=True)
            rev_g1 = st.slider("Revenue Growth — Yr 1 (%)", 0, 40, 12, key="fcff_g1") / 100
            rev_g2 = st.slider("Revenue Growth — Yr 2 (%)", 0, 40, 11, key="fcff_g2") / 100
            rev_g3 = st.slider("Revenue Growth — Yr 3 (%)", 0, 40, 10, key="fcff_g3") / 100
            rev_g4 = st.slider("Revenue Growth — Yr 4 (%)", 0, 35, 9, key="fcff_g4") / 100
            rev_g5 = st.slider("Revenue Growth — Yr 5 (%)", 0, 35, 8, key="fcff_g5") / 100
            ebit_margin = st.slider("EBIT Margin (%)", 1, 50, 15, key="fcff_ebit") / 100
            tax_rate = st.slider("Effective Tax Rate (%)", 10, 40, 25, key="fcff_tax") / 100
            da_pct = st.slider("D&A % of Revenue", 1, 15, 4, key="fcff_da") / 100
            capex_pct = st.slider("Capex % of Revenue", 1, 20, 6, key="fcff_capex") / 100
            wc_pct = st.slider("ΔWC % of Revenue", 0, 10, 2, key="fcff_wc") / 100
            wacc = st.slider("WACC (%)", 6, 20, 11, key="fcff_wacc") / 100
            tg_fcff = st.slider("Terminal Growth (%)", 2, 8, 4, key="fcff_tg") / 100

        result = run_fcff_dcf(
            revenue_base_cr, [rev_g1, rev_g2, rev_g3, rev_g4, rev_g5],
            ebit_margin, tax_rate, da_pct, capex_pct, wc_pct,
            wacc, tg_fcff, net_debt_cr, shares
        )
        intrinsic = result["value_per_share"]
        upside = ((intrinsic - current_price) / current_price) * 100 if current_price else 0

        with right:
            c1, c2, c3 = st.columns(3)
            with c1:
                metric_card("Current Price", f"₹{current_price:,.0f}")
            with c2:
                metric_card("Intrinsic Value", f"₹{intrinsic:,.0f}", "up" if upside > 0 else "down")
            with c3:
                metric_card("Upside / Downside", f"{upside:+.1f}%", "up" if upside > 0 else "down")

            vclass, vtext = verdict(upside)
            st.markdown(f'<div class="verdict-banner {vclass}">{vtext}</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown('<div class="section-label">Value Bridge (₹ Cr)</div>', unsafe_allow_html=True)
            bridge = pd.DataFrame({
                "Component": ["PV of FCFFs", "PV of Terminal Value", "Enterprise Value", "Less: Net Debt", "Equity Value"],
                "₹ Cr": [f"₹{result['pv_fcffs']:,.0f}", f"₹{result['pv_tv']:,.0f}",
                         f"₹{result['enterprise_value']:,.0f}", f"₹{net_debt_cr:,.0f}",
                         f"₹{result['equity_value']:,.0f}"],
            })
            st.dataframe(bridge, hide_index=True, use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-label">Sensitivity — Value/Share (₹) | WACC vs Terminal Growth</div>', unsafe_allow_html=True)
            wacc_range = [wacc - 0.02, wacc - 0.01, wacc, wacc + 0.01, wacc + 0.02]
            tgr_range = [tg_fcff - 0.01, tg_fcff, tg_fcff + 0.01, tg_fcff + 0.02]
            rows = []
            for w in wacc_range:
                row = {}
                for tg in tgr_range:
                    if w <= tg:
                        row[f"TGR {tg*100:.1f}%"] = "N/A"
                        continue
                    r = run_fcff_dcf(revenue_base_cr, [rev_g1, rev_g2, rev_g3, rev_g4, rev_g5],
                                      ebit_margin, tax_rate, da_pct, capex_pct, wc_pct,
                                      w, tg, net_debt_cr, shares)
                    row[f"TGR {tg*100:.1f}%"] = f"₹{r['value_per_share']:,.0f}"
                rows.append(row)
            sens_df = pd.DataFrame(rows, index=[f"WACC {w*100:.1f}%" for w in wacc_range])
            st.dataframe(sens_df, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — FCFE
    # ══════════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown(
            '<div class="model-note">Free Cash Flow to Equity, discounted at the cost '
            'of equity (CAPM). Values equity directly — skips WACC and net debt '
            'adjustments. Useful cross-check against FCFF.</div>', unsafe_allow_html=True)

        left, right = st.columns([1, 1.4])
        with left:
            st.markdown('<div class="section-label">Assumptions</div>', unsafe_allow_html=True)
            fe_g1 = st.slider("Revenue Growth — Yr 1 (%)", 0, 40, 12, key="fcfe_g1") / 100
            fe_g2 = st.slider("Revenue Growth — Yr 2 (%)", 0, 40, 11, key="fcfe_g2") / 100
            fe_g3 = st.slider("Revenue Growth — Yr 3 (%)", 0, 40, 10, key="fcfe_g3") / 100
            fe_g4 = st.slider("Revenue Growth — Yr 4 (%)", 0, 35, 9, key="fcfe_g4") / 100
            fe_g5 = st.slider("Revenue Growth — Yr 5 (%)", 0, 35, 8, key="fcfe_g5") / 100
            net_margin = st.slider("Net Margin (%)", 1, 40, 12, key="fcfe_margin") / 100
            fe_da = st.slider("D&A % of Revenue", 1, 15, 4, key="fcfe_da") / 100
            fe_capex = st.slider("Capex % of Revenue", 1, 20, 6, key="fcfe_capex") / 100
            fe_wc = st.slider("ΔWC % of Revenue", 0, 10, 2, key="fcfe_wc") / 100
            net_borrow = st.slider("Net Borrowing % of Revenue", -10, 15, 1, key="fcfe_borrow") / 100
            tg_fcfe = st.slider("Terminal Growth (%)", 2, 8, 4, key="fcfe_tg") / 100
            st.markdown(f'<div class="data-note">Cost of equity (Ke) from CAPM: {ke*100:.1f}%</div>', unsafe_allow_html=True)

        if ke <= tg_fcfe:
            with right:
                st.error("Cost of equity must exceed terminal growth rate. Adjust assumptions.")
        else:
            result_fe = run_fcfe(
                revenue_base_cr, [fe_g1, fe_g2, fe_g3, fe_g4, fe_g5],
                net_margin, fe_da, fe_capex, fe_wc, net_borrow, ke, tg_fcfe, shares
            )
            intrinsic_fe = result_fe["value_per_share"]
            upside_fe = ((intrinsic_fe - current_price) / current_price) * 100 if current_price else 0

            with right:
                c1, c2, c3 = st.columns(3)
                with c1:
                    metric_card("Current Price", f"₹{current_price:,.0f}")
                with c2:
                    metric_card("Intrinsic Value", f"₹{intrinsic_fe:,.0f}", "up" if upside_fe > 0 else "down")
                with c3:
                    metric_card("Upside / Downside", f"{upside_fe:+.1f}%", "up" if upside_fe > 0 else "down")

                vclass, vtext = verdict(upside_fe)
                st.markdown(f'<div class="verdict-banner {vclass}">{vtext}</div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

                st.markdown('<div class="section-label">Projected FCFE (₹ Cr)</div>', unsafe_allow_html=True)
                fe_table = pd.DataFrame({
                    "Year": [f"Year {i+1}" for i in range(5)],
                    "FCFE (₹ Cr)": [f"₹{v:,.0f}" for v in result_fe["fcfes"]],
                })
                st.dataframe(fe_table, hide_index=True, use_container_width=True)

                st.markdown("<br>", unsafe_allow_html=True)
                bridge_fe = pd.DataFrame({
                    "Component": ["PV of FCFEs", "PV of Terminal Value", "Equity Value (₹ Cr)"],
                    "₹ Cr": [f"₹{result_fe['pv_fcfes']:,.0f}", f"₹{result_fe['pv_tv']:,.0f}", f"₹{result_fe['equity_value']:,.0f}"],
                })
                st.dataframe(bridge_fe, hide_index=True, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3 — DDM
    # ══════════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown(
            '<div class="model-note">Dividend Discount Model (two-stage Gordon Growth). '
            'Values equity as the present value of future dividends — most meaningful '
            'for mature, steady dividend payers (e.g. banks, utilities, FMCG).</div>',
            unsafe_allow_html=True)

        if dps0 <= 0:
            st.warning(f"{company_name} does not currently pay a dividend (or yfinance has no dividend data). "
                       "DDM is not meaningful for non-dividend-paying companies — try FCFF, FCFE, or RIM instead.")
        else:
            left, right = st.columns([1, 1.4])
            with left:
                st.markdown('<div class="section-label">Assumptions</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="data-note">Current annual DPS: ₹{dps0:.2f}</div>', unsafe_allow_html=True)
                growth_stage1 = st.slider("Dividend Growth — Stage 1 (%)", 0, 30, 8, key="ddm_g1") / 100
                years_stage1 = st.slider("Stage 1 Length (years)", 3, 10, 5, key="ddm_years")
                tg_ddm = st.slider("Terminal Growth (%)", 1, 8, 4, key="ddm_tg") / 100
                st.markdown(f'<div class="data-note">Cost of equity (Ke) from CAPM: {ke*100:.1f}%</div>', unsafe_allow_html=True)

            if ke <= tg_ddm:
                with right:
                    st.error("Cost of equity must exceed terminal growth rate. Adjust assumptions.")
            else:
                result_ddm = run_ddm(dps0, growth_stage1, years_stage1, tg_ddm, ke)
                intrinsic_ddm = result_ddm["value_per_share"]
                upside_ddm = ((intrinsic_ddm - current_price) / current_price) * 100 if current_price else 0

                with right:
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        metric_card("Current Price", f"₹{current_price:,.0f}")
                    with c2:
                        metric_card("Intrinsic Value", f"₹{intrinsic_ddm:,.0f}", "up" if upside_ddm > 0 else "down")
                    with c3:
                        metric_card("Upside / Downside", f"{upside_ddm:+.1f}%", "up" if upside_ddm > 0 else "down")

                    vclass, vtext = verdict(upside_ddm)
                    st.markdown(f'<div class="verdict-banner {vclass}">{vtext}</div>', unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)

                    st.markdown('<div class="section-label">Projected Dividends (₹/share)</div>', unsafe_allow_html=True)
                    div_table = pd.DataFrame({
                        "Year": [f"Year {i+1}" for i in range(years_stage1)],
                        "DPS (₹)": [f"₹{d:.2f}" for d in result_ddm["divs"]],
                    })
                    st.dataframe(div_table, hide_index=True, use_container_width=True)

                    st.markdown("<br>", unsafe_allow_html=True)
                    bridge_ddm = pd.DataFrame({
                        "Component": ["PV of Stage-1 Dividends", "PV of Terminal Value", "Value per Share"],
                        "₹": [f"₹{result_ddm['pv_divs']:.2f}", f"₹{result_ddm['pv_tv']:.2f}", f"₹{result_ddm['value_per_share']:.2f}"],
                    })
                    st.dataframe(bridge_ddm, hide_index=True, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 4 — RESIDUAL INCOME MODEL
    # ══════════════════════════════════════════════════════════════════════════
    with tab4:
        st.markdown(
            '<div class="model-note">Residual Income Model — values equity as current '
            'book value plus the present value of future "excess" returns above the '
            'cost of equity. Works well for banks and financials where FCFF/FCFE '
            'break down.</div>', unsafe_allow_html=True)

        if bvps0 <= 0:
            st.warning(f"No book value per share data available for {company_name} — RIM cannot be computed.")
        else:
            left, right = st.columns([1, 1.4])
            with left:
                st.markdown('<div class="section-label">Assumptions</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="data-note">Current Book Value/Share: ₹{bvps0:.2f}</div>', unsafe_allow_html=True)
                roe_assumption = st.slider("Sustainable ROE (%)", 1.0, 40.0, max(current_roe*100, 1.0), 0.5, key="rim_roe") / 100
                book_growth = st.slider("Book Value Growth (%)", 0.0, 25.0, 8.0, 0.5, key="rim_bvg") / 100
                tg_rim = st.slider("Terminal Growth (%)", 1.0, 8.0, 4.0, 0.5, key="rim_tg") / 100
                rim_years = st.slider("Forecast Horizon (years)", 3, 10, 5, key="rim_years")
                st.markdown(f'<div class="data-note">Cost of equity (Ke) from CAPM: {ke*100:.1f}%</div>', unsafe_allow_html=True)

            if ke <= tg_rim:
                with right:
                    st.error("Cost of equity must exceed terminal growth rate. Adjust assumptions.")
            else:
                result_rim = run_rim(bvps0, roe_assumption, ke, book_growth, tg_rim, rim_years)
                intrinsic_rim = result_rim["value_per_share"]
                upside_rim = ((intrinsic_rim - current_price) / current_price) * 100 if current_price else 0

                with right:
                    if roe_assumption <= ke:
                        st.info(f"Assumed ROE ({roe_assumption*100:.1f}%) is at or below cost of equity "
                                f"({ke*100:.1f}%) — residual income is zero or negative, so value sits at "
                                "or below book value. This is a valid (if unexciting) result.")

                    c1, c2, c3 = st.columns(3)
                    with c1:
                        metric_card("Current Price", f"₹{current_price:,.0f}")
                    with c2:
                        metric_card("Intrinsic Value", f"₹{intrinsic_rim:,.0f}", "up" if upside_rim > 0 else "down")
                    with c3:
                        metric_card("Upside / Downside", f"{upside_rim:+.1f}%", "up" if upside_rim > 0 else "down")

                    vclass, vtext = verdict(upside_rim)
                    st.markdown(f'<div class="verdict-banner {vclass}">{vtext}</div>', unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)

                    st.markdown('<div class="section-label">Projected Residual Income (₹/share)</div>', unsafe_allow_html=True)
                    ri_table = pd.DataFrame({
                        "Year": [f"Year {i+1}" for i in range(rim_years)],
                        "Book Value/Share (₹)": [f"₹{b:.2f}" for b in result_rim["bvs"]],
                        "Residual Income (₹)": [f"₹{r:.2f}" for r in result_rim["ris"]],
                    })
                    st.dataframe(ri_table, hide_index=True, use_container_width=True)

                    st.markdown("<br>", unsafe_allow_html=True)
                    bridge_rim = pd.DataFrame({
                        "Component": ["Current Book Value/Share", "PV of Residual Income", "PV of Terminal Value", "Value per Share"],
                        "₹": [f"₹{bvps0:.2f}", f"₹{result_rim['pv_ris']:.2f}", f"₹{result_rim['pv_tv']:.2f}", f"₹{result_rim['value_per_share']:.2f}"],
                    })
                    st.dataframe(bridge_rim, hide_index=True, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<p class="data-note">Data sourced from Yahoo Finance via yfinance. '
        'Cost of equity computed via CAPM using live beta. '
        'This model is for illustrative and educational purposes only and does not constitute investment advice.</p>',
        unsafe_allow_html=True
    )
