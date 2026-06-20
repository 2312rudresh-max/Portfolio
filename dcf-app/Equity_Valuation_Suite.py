import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import math

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Equity Valuation Suite",
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

    /* ── Top-level panel selector (Intrinsic / Relative / Option) ── */
    .panel-tab-row {
        display: flex;
        gap: 0.6rem;
        margin-bottom: 1.5rem;
    }
    .panel-pill {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.78rem;
        letter-spacing: 0.05em;
        padding: 0.55rem 1.1rem;
        border-radius: 4px;
        border: 1px solid #2a2a2a;
        background: #141414;
        color: #777;
    }
    .panel-pill.active {
        border-color: #00c896;
        color: #00c896;
        background: #0a2e1f;
    }

    /* ── Slider impact meter ── */
    .slider-meter-wrap {
        margin: -0.6rem 0 1.1rem 0;
    }
    .slider-meter-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.62rem;
        color: #555;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.25rem;
        display: flex;
        justify-content: space-between;
    }
    .slider-meter-bar {
        height: 6px;
        border-radius: 3px;
        background: linear-gradient(to right, #ff4d4d, #f0b429, #00c896);
        position: relative;
    }
    .slider-meter-cursor {
        position: absolute;
        top: -4px;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background: #fff;
        border: 2px solid #444;
        transform: translateX(-50%);
        transition: left 0.2s ease;
    }
    .slider-meter-tip {
        font-family: 'Inter', sans-serif;
        font-size: 0.72rem;
        color: #888;
        margin-top: 0.3rem;
        line-height: 1.4;
    }

    /* ── Method explainer card ── */
    .method-explainer {
        background: #111;
        border: 1px solid #1e1e1e;
        border-radius: 6px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1.4rem;
    }
    .method-explainer-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.85rem;
        color: #00c896;
        font-weight: 600;
        margin-bottom: 0.5rem;
        letter-spacing: 0.05em;
    }
    .method-explainer-body {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: #aaa;
        line-height: 1.7;
    }
    .method-explainer-body b { color: #e8e8e8; }

    /* ── Value chain ── */
    .vchain-wrap {
        display: flex;
        align-items: stretch;
        gap: 0;
        margin: 1rem 0;
        overflow-x: auto;
    }
    .vchain-node {
        background: #161616;
        border: 1px solid #2a2a2a;
        border-radius: 4px;
        padding: 0.9rem 1rem;
        min-width: 140px;
        flex: 1;
    }
    .vchain-node-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.65rem;
        color: #555;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.4rem;
    }
    .vchain-node-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.82rem;
        color: #e8e8e8;
        font-weight: 500;
        margin-bottom: 0.25rem;
    }
    .vchain-node-detail {
        font-family: 'Inter', sans-serif;
        font-size: 0.72rem;
        color: #666;
        line-height: 1.4;
    }
    .vchain-arrow {
        display: flex;
        align-items: center;
        padding: 0 0.3rem;
        color: #333;
        font-size: 1.1rem;
    }

    /* ── Sector popover ── */
    .sector-popover {
        background: #111;
        border: 1px solid #2a2a2a;
        border-radius: 6px;
        padding: 1rem 1.2rem;
        margin-top: 0.5rem;
    }
    .sector-popover-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        color: #00c896;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.6rem;
    }
    .sector-driver {
        font-family: 'Inter', sans-serif;
        font-size: 0.8rem;
        color: #aaa;
        padding: 0.3rem 0;
        border-bottom: 1px solid #1a1a1a;
        line-height: 1.5;
    }
    .sector-driver:last-child { border-bottom: none; }
    .sector-driver b { color: #e8e8e8; }
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


@st.cache_data(ttl=3600)
def fetch_universe_multiples(tickers: dict):
    """Fetch key multiples for the whole Nifty 50 universe. Cached for 1 hour."""
    rows = []
    for name, tkr in tickers.items():
        try:
            info = yf.Ticker(tkr).info
            rows.append({
                "Company": name,
                "Sector": info.get("sector", "Unknown"),
                "Price": info.get("currentPrice") or info.get("regularMarketPrice") or np.nan,
                "P/E": info.get("trailingPE"),
                "P/B": info.get("priceToBook"),
                "EV/EBITDA": info.get("enterpriseToEbitda"),
                "P/S": info.get("priceToSalesTrailing12Months"),
                "EPS": info.get("trailingEps"),
                "BVPS": info.get("bookValue"),
                "RevPerShare": info.get("revenuePerShare"),
                "EBITDA": info.get("ebitda"),
                "TotalDebt": info.get("totalDebt"),
                "TotalCash": info.get("totalCash"),
                "Shares": info.get("sharesOutstanding"),
            })
        except Exception:
            continue
    return pd.DataFrame(rows)


@st.cache_data(ttl=3600)
def fetch_historical_volatility(ticker: str):
    """Annualized volatility of daily log returns over the last 1 year."""
    hist = yf.Ticker(ticker).history(period="1y")
    if hist.empty or len(hist) < 30:
        return None
    log_returns = np.log(hist["Close"] / hist["Close"].shift(1)).dropna()
    return float(log_returns.std() * np.sqrt(252))


def norm_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def black_scholes(S, K, T, r, sigma, option_type="call"):
    if sigma <= 0 or T <= 0:
        intrinsic = max(S - K, 0) if option_type == "call" else max(K - S, 0)
        return intrinsic, 0.0, 0.0, 0.0
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    if option_type == "call":
        price = S * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)
        delta = norm_cdf(d1)
    else:
        price = K * math.exp(-r * T) * norm_cdf(-d2) - S * norm_cdf(-d1)
        delta = norm_cdf(d1) - 1
    return price, delta, d1, d2


def merton_model(equity_value, debt_value, sigma_equity, r, T):
    V0 = equity_value + debt_value
    if V0 <= 0 or debt_value <= 0:
        return None
    sigma_V = sigma_equity * (equity_value / V0)
    if sigma_V <= 0:
        return None

    price, delta, d1, d2 = black_scholes(V0, debt_value, T, r, sigma_V, "call")

    dd = (math.log(V0 / debt_value) + (r - 0.5 * sigma_V ** 2) * T) / (sigma_V * math.sqrt(T))
    pd_default = norm_cdf(-dd)

    return {
        "asset_value": V0,
        "asset_vol": sigma_V,
        "implied_equity": price,
        "delta": delta,
        "distance_to_default": dd,
        "prob_default": pd_default,
    }


def safe_get(df, keys, default=None):
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


# ── Slider impact meter ─────────────────────────────────────────────────────
def slider_meter(tip: str, value: float, min_val: float, max_val: float,
                  direction: str = "positive"):
    """Red→green gradient bar with a cursor showing how this slider moves value."""
    pct = (value - min_val) / (max_val - min_val) if max_val != min_val else 0.5
    pct = max(0.0, min(1.0, pct))
    cursor_pct = pct * 100 if direction == "positive" else (1 - pct) * 100
    st.markdown(f"""
    <div class="slider-meter-wrap">
        <div class="slider-meter-label">
            <span>Lowers Value</span><span>Raises Value</span>
        </div>
        <div class="slider-meter-bar">
            <div class="slider-meter-cursor" style="left:{cursor_pct:.1f}%"></div>
        </div>
        <div class="slider-meter-tip">💡 {tip}</div>
    </div>""", unsafe_allow_html=True)


# ── Method explainer card ────────────────────────────────────────────────────
def method_explainer(title: str, body: str):
    st.markdown(f"""
    <div class="method-explainer">
        <div class="method-explainer-title">🧮 {title}</div>
        <div class="method-explainer-body">{body}</div>
    </div>""", unsafe_allow_html=True)


# ── Value chain data ─────────────────────────────────────────────────────────
VALUE_CHAINS = {
    "Reliance Industries": [
        ("Upstream", "Oil & Gas E&P", "Crude at ~$75–85/bbl; KG-D6 domestic gas"),
        ("Refining", "Jamnagar Refinery", "Crude-to-product spread ~$8–12/bbl GRM"),
        ("Petrochem", "Polymers & Fibres", "Naphtha → PE/PP; margin ~₹8–12k/tonne"),
        ("Retail", "Reliance Retail", "B2C markup across grocery, fashion, electronics"),
        ("Digital", "Jio Platforms", "ARPU ~₹195/month; ~480M subscribers"),
    ],
    "TCS": [
        ("Talent", "Engineering Hiring", "Fresher CTC ~₹3.5–7L; lateral ~₹12–25L"),
        ("Delivery", "IT Services", "Revenue/employee ~$35–40k/year"),
        ("Contracts", "Client Deals", "TCV wins; fixed-price & T&M models"),
        ("Margins", "EBIT ~24–25%", "Utilisation ~85–87% is key lever"),
        ("Revenue", "Client Billing", "Billed in USD/GBP; FX tailwind/headwind ±2–3%"),
    ],
    "HDFC Bank": [
        ("Deposits", "CASA + Term", "CASA ratio ~42%; cost of funds ~4.5%"),
        ("Lending", "Retail & Corporate", "Yield on advances ~9.5–10.5%"),
        ("NIM", "Spread", "NIM ~3.9–4.1%; key profitability driver"),
        ("Provisions", "Credit Cost", "PCR ~75%; NPA ~1.3% gross"),
        ("Fee Income", "Forex, Cards, WM", "Non-interest income ~20% of revenue"),
    ],
    "Infosys": [
        ("Talent", "Campus + Lateral", "~3.3L employees; attrition ~12–14%"),
        ("Delivery", "IT & BPM", "Onsite/offshore mix: ~30%/70%"),
        ("Deals", "Large Deal TCV", "Cobalt, Topaz AI frameworks drive deals"),
        ("Margins", "EBIT ~20–21%", "Pyramid optimisation & automation key"),
        ("Revenue", "USD Billing", "FY24 revenue ~$18.6B; guidance ~1–3% growth"),
    ],
    "ICICI Bank": [
        ("Deposits", "Retail + Corporate", "CASA ~45%; deposit cost ~4.3%"),
        ("Advances", "Retail & SME focus", "Retail mix ~55%; yield ~10%"),
        ("NIM", "Core spread", "NIM ~4.4%; better than peer avg"),
        ("Provisions", "Asset Quality", "GNPA ~2.2%; well-provisioned"),
        ("Subsidiaries", "ICICI Sec, Life, GI", "Significant value; listed separately"),
    ],
    "Hindustan Unilever": [
        ("Procurement", "Agri Commodities", "Palm oil, copra, tea — volatile input costs"),
        ("Manufacturing", "35+ factories", "Gross margin ~50%; scale advantage"),
        ("Distribution", "9M+ retail outlets", "Direct reach + super-stockist network"),
        ("Marketing", "A&P ~10% of sales", "Brand investment sustains premium pricing"),
        ("Revenue", "B2C FMCG", "Volume × price; rural/urban mix matters"),
    ],
    "Maruti Suzuki": [
        ("Sourcing", "Auto Components", "~70% localisation; RM ~65% of cost"),
        ("Manufacturing", "Manesar + Gujarat", "Capacity ~2.25M units/year"),
        ("Distribution", "ARENA + NEXA", "3,500+ outlets; dealer margin ~2–3%"),
        ("ASC", "After-Sales", "Service + spares margin-rich, recurring"),
        ("Revenue", "Vehicle Sales", "ASP ~₹6.8L; mix shift to SUVs ongoing"),
    ],
    "Bajaj Finance": [
        ("Borrowing", "NCD + Bank Lines", "Cost of funds ~7.5–8%"),
        ("Underwriting", "Consumer + SME Loans", "Yield ~16–18%; risk-based pricing"),
        ("Cross-sell", "Insurance + Cards", "Fee income boosts ROA"),
        ("Provisions", "ECL Model", "Stage 3 ~1.1%; PCR ~60%"),
        ("Revenue", "NII + Fees", "NIM ~10%+; ROE ~22–24%"),
    ],
    "Bharti Airtel": [
        ("Spectrum", "4G/5G Bands", "Spectrum cost amortised over licence period"),
        ("Network", "Tower + Fibre", "Indus Towers partnership; capex-heavy"),
        ("ARPU", "Tariff Hikes", "India mobile ARPU ~₹208; target ₹300+"),
        ("Africa", "14 Countries", "~25% of revenue; USD-denominated upside"),
        ("Revenue", "Mobile + Broadband", "Postpaid mix rising; churn ~1.5%/month"),
    ],
    "ITC": [
        ("Sourcing", "Tobacco Leaf + Agri", "Farmer procurement via e-Choupal network"),
        ("Cigarettes", "FMCG-Cigarettes", "~80% of profit; high excise tax burden"),
        ("FMCG-Others", "Foods, Personal Care", "Growing fast but lower margin than cigarettes"),
        ("Paperboards", "Packaging & Paper", "Capital-intensive; cyclical pulp prices"),
        ("Revenue", "Diversified Mix", "Cigarettes fund FMCG expansion investments"),
    ],
    "Tata Motors": [
        ("Sourcing", "Steel + Components", "JLR sources globally; CV/PV domestic-heavy"),
        ("Manufacturing", "India + UK Plants", "JLR (Solihull, Halewood) + domestic CV/PV"),
        ("EV Transition", "Battery & EV Lineup", "Domestic EV leader; JLR going electric by 2030"),
        ("Distribution", "Dealer Network", "Separate CV, PV, EV, and JLR channels"),
        ("Revenue", "Global + Domestic", "JLR ~70% of consolidated revenue, GBP-denominated"),
    ],
    "Sun Pharma": [
        ("R&D", "Specialty + Generics", "R&D spend ~7-8% of revenue"),
        ("Manufacturing", "API + Formulations", "Vertically integrated; US FDA compliance critical"),
        ("US Generics", "ANDA Pipeline", "Para IV filings drive high-margin opportunities"),
        ("Domestic Branded", "India Market Leader", "Branded generics; doctor-led prescription model"),
        ("Revenue", "Global Pharma Sales", "US + India + Emerging markets + Specialty"),
    ],
    "default": [
        ("Inputs", "Raw Materials / Labour", "Key input costs vary by sector"),
        ("Operations", "Core Business Activity", "Value-add at this stage drives margins"),
        ("Distribution", "Channel to Market", "Logistics and channel costs"),
        ("Marketing", "Brand & Sales", "CAC and brand investment"),
        ("Revenue", "End Customer", "Final price realisation and margin"),
    ],
}

# ── Sector key drivers ────────────────────────────────────────────────────────
SECTOR_DRIVERS = {
    "Technology": [
        ("Revenue Growth", "Demand for digital transformation, cloud migration, and AI deals drives top-line. Watch deal TCV and pipeline."),
        ("Employee Utilisation", "Billed hours / available hours. ~85–87% is healthy; below 82% compresses margins fast."),
        ("Attrition Rate", "High attrition raises hiring and training costs, disrupts client delivery. Sub-15% is preferred."),
        ("Currency (USD/INR)", "Most revenue billed in USD. Every ₹1 depreciation in INR adds ~40–60bps to EBIT margin."),
        ("Deal Wins & Ramp-up", "Large deal TCV signals future revenue visibility. Ramp-up lag of 2–4 quarters is normal."),
    ],
    "Financial Services": [
        ("Net Interest Margin (NIM)", "Spread between lending yield and cost of funds. Higher NIM = more profitable core business."),
        ("Asset Quality (NPA)", "Gross and net NPA ratios. Rising NPAs signal credit stress and require higher provisions."),
        ("CASA Ratio", "Current + Savings deposits as % of total. Higher CASA = lower cost of funds = better margins."),
        ("Credit Growth", "Loan book expansion drives revenue, but must be matched with risk controls."),
        ("Regulatory Capital (CAR)", "Capital Adequacy Ratio must stay above 11.5% (RBI mandate). Constrains growth speed."),
    ],
    "Consumer Defensive": [
        ("Volume Growth", "Units sold across categories. Even 1–2% volume growth in FMCG signals strong brand health."),
        ("Raw Material Costs", "Palm oil, copra, wheat, sugar etc. Input inflation squeezes gross margins directly."),
        ("Rural vs Urban Mix", "Rural recovery drives volume in mass categories. Urban premiumisation lifts ASP."),
        ("Distribution Reach", "Wider direct reach = faster new product rollout and lower dependence on wholesale."),
        ("A&P Spend", "Advertising & Promotion as % of sales. Cutting A&P boosts short-term margins but erodes brand equity."),
    ],
    "Energy": [
        ("Crude Oil Price", "Global benchmark (Brent/WTI). Drives upstream realisations and downstream refining economics."),
        ("Gross Refining Margin (GRM)", "Revenue from refined products minus crude cost per barrel. Key profitability metric for refiners."),
        ("Petrochemical Spreads", "Difference between polymer/fibre prices and naphtha feedstock. Cyclical and volatile."),
        ("Government Policy / Subsidy", "APM pricing, subsidy sharing, export duty — heavily influences net realisations for PSU oil cos."),
        ("Capex Cycle", "Large upstream and refinery capex depresses FCF for years but builds long-term capacity."),
    ],
    "Industrials": [
        ("Order Book & Inflows", "Fresh orders indicate future revenue. Book-to-bill > 1x signals pipeline strength."),
        ("Working Capital Cycle", "Long project cycles tie up cash. Debtor days and cash conversion are critical."),
        ("Raw Material (Steel/Cement)", "Key input costs. RM as % of revenue ~60–70% for EPC companies."),
        ("Government Capex / Infra Spend", "Union Budget allocations to roads, railways, defence drive order inflows."),
        ("Execution Risk", "Project delays and cost overruns are the biggest margin risk for EPC contractors."),
    ],
    "Basic Materials": [
        ("Commodity Price Cycle", "Steel, aluminium, cement prices are globally/domestically driven. Highly cyclical."),
        ("Capacity Utilisation", "Higher utilisation spreads fixed costs. Industry-wide utilisation >80% typically lifts pricing."),
        ("Input Costs (Coking Coal, Iron Ore)", "For steel, coking coal is the swing cost. Australia/China dynamics matter."),
        ("China Demand & Exports", "China's steel/aluminium output directly impacts global prices and Indian realisations."),
        ("Debt Levels", "Capital-intensive sector; high leverage amplifies both upside in upcycles and stress in downcycles."),
    ],
    "Healthcare": [
        ("Domestic Formulations Growth", "India branded generics market. NLEM price controls cap growth on essential medicines."),
        ("US Generic Pipeline & ANDA Approvals", "USFDA filings and approvals determine US revenue trajectory. Para IVs are high-value."),
        ("USFDA Compliance Risk", "Warning letters and import alerts can shut down key plants — biggest de-rating risk."),
        ("API Self-Sufficiency", "In-house API manufacturing improves margins and supply security."),
        ("R&D Spend", "Investment in specialty/complex generics and biosimilars is the key long-term value driver."),
    ],
    "Communication Services": [
        ("ARPU (Avg Revenue Per User)", "Primary profitability lever in telecom. Every ₹10 ARPU rise = significant EBITDA jump at scale."),
        ("Subscriber Market Share", "4G/5G subscriber additions and churn. Postpaid mix is more valuable than prepaid."),
        ("5G Capex & Monetisation", "Massive 5G rollout capex must eventually be monetised via enterprise and FWA."),
        ("Spectrum Cost & Debt", "High spectrum payments inflate debt. EBITDA-to-debt ratio is key solvency watch."),
        ("Africa Operations", "USD revenue from African markets provides diversification and growth optionality."),
    ],
    "Consumer Cyclical": [
        ("Vehicle Volume & Mix", "Units sold across segments. SUV/premium mix shift raises ASP and margins."),
        ("Rural Demand Cycle", "Two-wheelers and entry-level cars are rural-demand sensitive — monsoon and MSP matter."),
        ("Raw Material Costs", "Steel and aluminium are ~60–65% of vehicle cost. Commodity cycles directly hit margins."),
        ("New Model Pipeline", "Fresh launches sustain demand and enable pricing power. Ageing portfolio is a risk."),
        ("EV Transition Risk", "Pace of EV adoption and readiness of incumbent OEMs to compete in EVs is a structural watch."),
    ],
    "Utilities": [
        ("Regulated Returns", "RoE on regulated capital base (typically ~14-15.5% for power transmission/generation)."),
        ("Capacity Addition", "New plant commissioning drives the regulated asset base and future earnings."),
        ("PLF / Plant Availability", "Plant Load Factor and availability determine capacity charge recovery."),
        ("Fuel Cost Pass-through", "Coal/gas cost variations are typically passed through, limiting margin risk."),
        ("Renewable Transition", "Shift to renewables affects long-term asset mix and growth capital allocation."),
    ],
    "default": [
        ("Revenue Growth", "Top-line expansion is the primary driver of long-term equity value."),
        ("Margin Profile", "EBIT and net margins determine how much of revenue flows to shareholders."),
        ("Capital Efficiency", "Return on Capital Employed (ROCE) measures how well assets generate earnings."),
        ("Debt & Leverage", "High debt amplifies returns in good times but creates risk in downturns."),
        ("Competitive Moat", "Brand, scale, switching costs, or regulatory barriers protect pricing power over time."),
    ],
}


def render_value_chain(company_name: str):
    chain = VALUE_CHAINS.get(company_name, VALUE_CHAINS["default"])
    nodes_html = ""
    for i, (stage, label, detail) in enumerate(chain):
        arrow = '<div class="vchain-arrow">→</div>' if i < len(chain) - 1 else ""
        nodes_html += f"""
        <div class="vchain-node">
            <div class="vchain-node-title">{stage}</div>
            <div class="vchain-node-label">{label}</div>
            <div class="vchain-node-detail">{detail}</div>
        </div>{arrow}"""
    st.markdown(f'<div class="vchain-wrap">{nodes_html}</div>', unsafe_allow_html=True)


def render_sector_drivers(sector: str):
    drivers = SECTOR_DRIVERS.get(sector, SECTOR_DRIVERS["default"])
    drivers_html = "".join(
        f'<div class="sector-driver"><b>{name}</b> — {desc}</div>'
        for name, desc in drivers
    )
    st.markdown(f"""
    <div class="sector-popover">
        <div class="sector-popover-title">📊 Key Value Drivers — {sector}</div>
        {drivers_html}
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

    st.markdown('<div class="section-label" style="margin-top:1.5rem">Choose Your Lens</div>', unsafe_allow_html=True)
    panel_choice = st.radio(
        "",
        ["🏗️ Intrinsic Value", "⚖️ Relative Valuation", "🎲 Option Pricing"],
        label_visibility="collapsed",
    )

# ── Main ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">Equity Valuation Suite</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Intrinsic · Relative · Option-Based · Live Market Data · FCFF · FCFE · DDM · RIM · Multiples · Merton</div>', unsafe_allow_html=True)

with st.spinner(f"Fetching {company_name} financials..."):
    try:
        info, cf, income, balance = fetch_financials(ticker)
        fetch_ok = True
    except Exception as e:
        st.error(f"Could not fetch data for {ticker}: {e}")
        fetch_ok = False

if fetch_ok:
    current_price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
    shares = info.get("sharesOutstanding") or 1
    market_cap_cr = (current_price * shares) / 1e7
    beta = info.get("beta") or 1.0

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
        with st.expander("📊 Key Drivers", expanded=False):
            render_sector_drivers(sector)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander(f"🔗 {company_name} — Value Chain (How they make money)", expanded=False):
        st.markdown('<div class="section-label">Procurement → Operations → Distribution → Revenue</div>', unsafe_allow_html=True)
        render_value_chain(company_name)

    st.markdown("<br>", unsafe_allow_html=True)

    if panel_choice == "🏗️ Intrinsic Value":

        st.markdown('<div class="section-label">Intrinsic Value — Cash-Flow & Earnings-Based Models</div>', unsafe_allow_html=True)

        sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs(["FCFF · DCF", "FCFE", "DDM", "Residual Income"])

        with sub_tab1:
            method_explainer(
                "FCFF · Discounted Cash Flow",
                "Imagine the company is a machine that generates <b>free cash</b> every year after paying its bills, "
                "taxes, and reinvesting to grow. This model adds up all that future cash — but since cash tomorrow "
                "is worth less than cash today, we <b>discount</b> it back. "
                "The discount rate is <b>WACC</b> (what investors and lenders require as a return). "
                "If the discounted sum exceeds today's price, the stock is undervalued. "
                "<br><br><b>Best for:</b> Industrial, tech, consumer companies with visible capex and working capital cycles. "
                "<b>Sensitive to:</b> Revenue growth assumptions and WACC — small changes move value dramatically."
            )

            left, right = st.columns([1, 1.4])
            with left:
                st.markdown('<div class="section-label">Assumptions</div>', unsafe_allow_html=True)

                rev_g1 = st.slider("Revenue Growth — Yr 1 (%)", 0, 40, 12, key="fcff_g1") / 100
                slider_meter("Higher growth → more future cash → higher value", rev_g1*100, 0, 40, "positive")
                rev_g2 = st.slider("Revenue Growth — Yr 2 (%)", 0, 40, 11, key="fcff_g2") / 100
                slider_meter("Year 2 growth compounds on Year 1 — amplifies total cash", rev_g2*100, 0, 40, "positive")
                rev_g3 = st.slider("Revenue Growth — Yr 3 (%)", 0, 40, 10, key="fcff_g3") / 100
                slider_meter("Mid-cycle growth expectation", rev_g3*100, 0, 40, "positive")
                rev_g4 = st.slider("Revenue Growth — Yr 4 (%)", 0, 35, 9, key="fcff_g4") / 100
                slider_meter("Growth typically moderates as the company matures", rev_g4*100, 0, 35, "positive")
                rev_g5 = st.slider("Revenue Growth — Yr 5 (%)", 0, 35, 8, key="fcff_g5") / 100
                slider_meter("Year 5 feeds directly into the terminal value — high impact", rev_g5*100, 0, 35, "positive")
                ebit_margin = st.slider("EBIT Margin (%)", 1, 50, 15, key="fcff_ebit") / 100
                slider_meter("Profit left after all operating costs. Higher = more cash per ₹ of revenue", ebit_margin*100, 1, 50, "positive")
                tax_rate = st.slider("Effective Tax Rate (%)", 10, 40, 25, key="fcff_tax") / 100
                slider_meter("Higher tax eats into NOPAT (after-tax operating profit)", tax_rate*100, 10, 40, "negative")
                da_pct = st.slider("D&A % of Revenue", 1, 15, 4, key="fcff_da") / 100
                slider_meter("D&A is a non-cash add-back — higher D&A slightly boosts FCFF", da_pct*100, 1, 15, "positive")
                capex_pct = st.slider("Capex % of Revenue", 1, 20, 6, key="fcff_capex") / 100
                slider_meter("Cash spent on assets — reduces free cash flow directly", capex_pct*100, 1, 20, "negative")
                wc_pct = st.slider("ΔWC % of Revenue", 0, 10, 2, key="fcff_wc") / 100
                slider_meter("Cash tied up in inventory and receivables — higher WC = less free cash", wc_pct*100, 0, 10, "negative")
                wacc = st.slider("WACC (%)", 6, 20, 11, key="fcff_wacc") / 100
                slider_meter("Your required return — higher WACC shrinks value by discounting cash flows more aggressively", wacc*100, 6, 20, "negative")
                tg_fcff = st.slider("Terminal Growth (%)", 2, 8, 4, key="fcff_tg") / 100
                slider_meter("Growth assumed forever after Year 5 — small changes have outsized impact", tg_fcff*100, 2, 8, "positive")

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

        with sub_tab2:
            method_explainer(
                "FCFE · Free Cash Flow to Equity",
                "Similar to FCFF, but we only look at <b>cash that belongs to shareholders</b> after the company "
                "has also repaid debt obligations and borrowed new money. "
                "We discount using the <b>Cost of Equity (Ke)</b> from CAPM — the return shareholders demand. "
                "FCFE is especially useful as a cross-check against FCFF when the company carries significant debt. "
                "<br><br><b>Key difference from FCFF:</b> Net borrowing is explicitly modelled — if the company borrows "
                "more, equity holders get that cash too. <b>Best for:</b> Leveraged companies where the debt structure matters."
            )

            left, right = st.columns([1, 1.4])
            with left:
                st.markdown('<div class="section-label">Assumptions</div>', unsafe_allow_html=True)

                fe_g1 = st.slider("Revenue Growth — Yr 1 (%)", 0, 40, 12, key="fcfe_g1") / 100
                slider_meter("More revenue → more net income → more cash for equity holders", fe_g1*100, 0, 40, "positive")
                fe_g2 = st.slider("Revenue Growth — Yr 2 (%)", 0, 40, 11, key="fcfe_g2") / 100
                slider_meter("Compounding effect — Year 2 growth builds on Year 1 base", fe_g2*100, 0, 40, "positive")
                fe_g3 = st.slider("Revenue Growth — Yr 3 (%)", 0, 40, 10, key="fcfe_g3") / 100
                slider_meter("Mid-cycle growth rate", fe_g3*100, 0, 40, "positive")
                fe_g4 = st.slider("Revenue Growth — Yr 4 (%)", 0, 35, 9, key="fcfe_g4") / 100
                slider_meter("Growth moderates as business scales", fe_g4*100, 0, 35, "positive")
                fe_g5 = st.slider("Revenue Growth — Yr 5 (%)", 0, 35, 8, key="fcfe_g5") / 100
                slider_meter("Feeds into terminal value — has outsized long-run impact", fe_g5*100, 0, 35, "positive")
                net_margin = st.slider("Net Margin (%)", 1, 40, 12, key="fcfe_margin") / 100
                slider_meter("Profit after all costs including interest and tax — FCFE's top driver", net_margin*100, 1, 40, "positive")
                fe_da = st.slider("D&A % of Revenue", 1, 15, 4, key="fcfe_da") / 100
                slider_meter("Non-cash charge added back — slightly boosts FCFE", fe_da*100, 1, 15, "positive")
                fe_capex = st.slider("Capex % of Revenue", 1, 20, 6, key="fcfe_capex") / 100
                slider_meter("Cash spent building assets — directly reduces FCFE", fe_capex*100, 1, 20, "negative")
                fe_wc = st.slider("ΔWC % of Revenue", 0, 10, 2, key="fcfe_wc") / 100
                slider_meter("Cash locked in operations — higher WC means less free cash for equity", fe_wc*100, 0, 10, "negative")
                net_borrow = st.slider("Net Borrowing % of Revenue", -10, 15, 1, key="fcfe_borrow") / 100
                slider_meter("Positive = company is borrowing more, adding cash to equity. Negative = repaying debt.", net_borrow*100, -10, 15, "positive")
                tg_fcfe = st.slider("Terminal Growth (%)", 2, 8, 4, key="fcfe_tg") / 100
                slider_meter("Perpetual growth rate after the forecast period — powerful lever", tg_fcfe*100, 2, 8, "positive")
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

        with sub_tab3:
            method_explainer(
                "DDM · Dividend Discount Model",
                "This model says: a share is worth exactly the <b>present value of all future dividends</b> it will pay you. "
                "Stage 1 is a high-growth phase where dividends grow faster. Stage 2 is the <b>terminal/steady-state</b> "
                "where they grow at a stable rate forever. "
                "We discount all those dividends at the cost of equity (Ke). "
                "<br><br><b>Best for:</b> Mature dividend-paying companies — PSU banks, utilities, FMCG giants. "
                "<b>Not useful for:</b> Growth companies that don't pay dividends (DDM will warn you). "
                "<b>Sensitive to:</b> The gap between Ke and terminal growth — narrow it and value explodes."
            )

            if dps0 <= 0:
                st.warning(f"{company_name} does not currently pay a dividend (or yfinance has no dividend data). "
                           "DDM is not meaningful for non-dividend-paying companies — try FCFF, FCFE, or RIM instead.")
            else:
                left, right = st.columns([1, 1.4])
                with left:
                    st.markdown('<div class="section-label">Assumptions</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="data-note">Current annual DPS: ₹{dps0:.2f}</div>', unsafe_allow_html=True)
                    growth_stage1 = st.slider("Dividend Growth — Stage 1 (%)", 0, 30, 8, key="ddm_g1") / 100
                    slider_meter("Faster dividend growth in Stage 1 means larger early payments, raising present value", growth_stage1*100, 0, 30, "positive")
                    years_stage1 = st.slider("Stage 1 Length (years)", 3, 10, 5, key="ddm_years")
                    slider_meter("More years at high growth = more value from Stage 1 dividends before terminal value kicks in", float(years_stage1), 3, 10, "positive")
                    tg_ddm = st.slider("Terminal Growth (%)", 1, 8, 4, key="ddm_tg") / 100
                    slider_meter("The growth rate assumed forever — the closer to Ke, the higher the value (but watch for blow-ups!)", tg_ddm*100, 1, 8, "positive")
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

        with sub_tab4:
            method_explainer(
                "RIM · Residual Income Model",
                "Start with what the company is <b>worth on paper today</b> (book value per share). "
                "Then ask: does it earn <b>more than shareholders require</b>? "
                "If ROE > Ke, the extra return is 'residual income' — real value creation above and beyond what's expected. "
                "Add the present value of all future residual income to book value and you get intrinsic value. "
                "<br><br><b>Best for:</b> Banks and financial companies where FCFF/FCFE are not meaningful because "
                "debt is a raw material, not just financing. <b>Key insight:</b> A company earning exactly its cost of "
                "equity is worth exactly book value — no more, no less."
            )

            if bvps0 <= 0:
                st.warning(f"No book value per share data available for {company_name} — RIM cannot be computed.")
            else:
                left, right = st.columns([1, 1.4])
                with left:
                    st.markdown('<div class="section-label">Assumptions</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="data-note">Current Book Value/Share: ₹{bvps0:.2f}</div>', unsafe_allow_html=True)
                    roe_assumption = st.slider("Sustainable ROE (%)", 1.0, 40.0, max(current_roe*100, 1.0), 0.5, key="rim_roe") / 100
                    slider_meter("ROE above Ke creates value. The wider the gap, the higher the intrinsic value above book.", roe_assumption*100, 1.0, 40.0, "positive")
                    book_growth = st.slider("Book Value Growth (%)", 0.0, 25.0, 8.0, 0.5, key="rim_bvg") / 100
                    slider_meter("Faster book value growth expands the base on which residual income is earned", book_growth*100, 0.0, 25.0, "positive")
                    tg_rim = st.slider("Terminal Growth (%)", 1.0, 8.0, 4.0, 0.5, key="rim_tg") / 100
                    slider_meter("Perpetual growth in residual income after the forecast period", tg_rim*100, 1.0, 8.0, "positive")
                    rim_years = st.slider("Forecast Horizon (years)", 3, 10, 5, key="rim_years")
                    slider_meter("Longer horizon captures more excess-return years explicitly", float(rim_years), 3, 10, "positive")
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

    elif panel_choice == "⚖️ Relative Valuation":

        st.markdown('<div class="section-label">Relative Valuation — Peer Multiple Comparison</div>', unsafe_allow_html=True)

        method_explainer(
            "Relative Valuation · Peer Multiples",
            "Instead of projecting cash flows, this model asks: <b>what are similar companies trading at?</b> "
            "It takes the median P/E, P/B, EV/EBITDA and P/S ratios of Nifty 50 sector peers, "
            "then applies those multiples to this company's own fundamentals (EPS, book value, EBITDA, revenue). "
            "The result is an <b>implied fair price</b> — what the market would pay if this stock were re-rated to peer levels. "
            "<br><br><b>Best for:</b> Quick sanity-checks and identifying mispricing within a sector. "
            "<b>Limitation:</b> Garbage in, garbage out — if the whole sector is overvalued, relative valuation won't tell you."
        )

        with st.spinner("Fetching sector peer multiples (first load may take a minute)..."):
            universe = fetch_universe_multiples(NIFTY50)

        my_sector = info.get("sector", "Unknown")
        peers = universe[(universe["Sector"] == my_sector) & (universe["Company"] != company_name)]

        if peers.empty or my_sector == "Unknown":
            st.warning(f"Not enough sector peer data available for {company_name} (sector: {my_sector}).")
        else:
            st.markdown(f'<div class="data-note">Sector: {my_sector} · {len(peers)} peer(s) found in Nifty 50</div>', unsafe_allow_html=True)

            def peer_median(col):
                vals = pd.to_numeric(peers[col], errors="coerce")
                vals = vals[vals > 0]
                return vals.median() if not vals.empty else None

            med_pe = peer_median("P/E")
            med_pb = peer_median("P/B")
            med_evebitda = peer_median("EV/EBITDA")
            med_ps = peer_median("P/S")

            eps = info.get("trailingEps")
            ebitda = info.get("ebitda")
            rev_per_share = info.get("revenuePerShare")

            implied = {}
            if med_pe and eps and eps > 0:
                implied["P/E"] = med_pe * eps
            if med_pb and bvps0 and bvps0 > 0:
                implied["P/B"] = med_pb * bvps0
            if med_ps and rev_per_share and rev_per_share > 0:
                implied["P/S"] = med_ps * rev_per_share
            if med_evebitda and ebitda and ebitda > 0 and shares:
                ev = med_evebitda * ebitda
                equity_val = ev - (net_debt_cr * 1e7)
                implied["EV/EBITDA"] = equity_val / shares

            left, right = st.columns([1, 1.4])

            with left:
                st.markdown('<div class="section-label">This Company vs Sector Median</div>', unsafe_allow_html=True)
                comp_table = pd.DataFrame({
                    "Multiple": ["P/E", "P/B", "EV/EBITDA", "P/S"],
                    company_name: [
                        f"{info.get('trailingPE'):.1f}x" if info.get("trailingPE") else "N/A",
                        f"{info.get('priceToBook'):.2f}x" if info.get("priceToBook") else "N/A",
                        f"{info.get('enterpriseToEbitda'):.1f}x" if info.get("enterpriseToEbitda") else "N/A",
                        f"{info.get('priceToSalesTrailing12Months'):.1f}x" if info.get("priceToSalesTrailing12Months") else "N/A",
                    ],
                    "Sector Median": [
                        f"{med_pe:.1f}x" if med_pe else "N/A",
                        f"{med_pb:.2f}x" if med_pb else "N/A",
                        f"{med_evebitda:.1f}x" if med_evebitda else "N/A",
                        f"{med_ps:.1f}x" if med_ps else "N/A",
                    ],
                })
                st.dataframe(comp_table, hide_index=True, use_container_width=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<div class="section-label">Sector Peers</div>', unsafe_allow_html=True)
                peer_display = peers[["Company", "P/E", "P/B", "EV/EBITDA", "P/S"]].copy()
                for col in ["P/E", "P/B", "EV/EBITDA", "P/S"]:
                    peer_display[col] = peer_display[col].apply(lambda v: f"{v:.1f}x" if pd.notna(v) else "N/A")
                st.dataframe(peer_display, hide_index=True, use_container_width=True)

            with right:
                if not implied:
                    st.warning("Could not compute implied price — insufficient peer or fundamental data.")
                else:
                    implied_avg = sum(implied.values()) / len(implied)
                    upside_rv = ((implied_avg - current_price) / current_price) * 100 if current_price else 0

                    c1, c2, c3 = st.columns(3)
                    with c1:
                        metric_card("Current Price", f"₹{current_price:,.0f}")
                    with c2:
                        metric_card("Implied Price (avg)", f"₹{implied_avg:,.0f}", "up" if upside_rv > 0 else "down")
                    with c3:
                        metric_card("Upside / Downside", f"{upside_rv:+.1f}%", "up" if upside_rv > 0 else "down")

                    vclass, vtext = verdict(upside_rv)
                    st.markdown(f'<div class="verdict-banner {vclass}">{vtext}</div>', unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)

                    st.markdown('<div class="section-label">Implied Price by Multiple (₹)</div>', unsafe_allow_html=True)
                    implied_table = pd.DataFrame({
                        "Multiple": list(implied.keys()),
                        "Peer Median": [
                            f"{med_pe:.1f}x" if k == "P/E" else
                            f"{med_pb:.2f}x" if k == "P/B" else
                            f"{med_evebitda:.1f}x" if k == "EV/EBITDA" else
                            f"{med_ps:.1f}x"
                            for k in implied.keys()
                        ],
                        "Implied Price (₹)": [f"₹{v:,.0f}" for v in implied.values()],
                    })
                    st.dataframe(implied_table, hide_index=True, use_container_width=True)

                    st.markdown(
                        "<p class=\"data-note\">Implied price = peer-median multiple × this company's "
                        "corresponding per-share fundamental (EPS, BVPS, revenue/share, or EBITDA-derived "
                        "equity value). Average across available multiples.</p>",
                        unsafe_allow_html=True)

    elif panel_choice == "🎲 Option Pricing":

        st.markdown('<div class="section-label">Option Pricing — Equity as a Call Option</div>', unsafe_allow_html=True)

        method_explainer(
            "Option Pricing · Merton / Black-Scholes",
            "Here's a mind-bending idea from Damodaran: <b>equity is a call option on the firm's assets</b>. "
            "The company's total assets are the 'underlying', total debt is the 'strike price', and shareholders "
            "only get paid after debtholders. If assets > debt, equity is in-the-money. If assets < debt, equity is worthless. "
            "The <b>Merton/KMV model</b> uses this to estimate the probability of default and implied equity value. "
            "<br><br>The <b>Black-Scholes calculator</b> below lets you price any call or put option on this stock. "
            "<b>Best for:</b> Distressed companies, credit analysis, or understanding the equity risk premium. "
            "<b>For low-debt firms:</b> equity ≈ enterprise value and the option framing adds limited insight."
        )

        hist_vol = fetch_historical_volatility(ticker)

        if hist_vol is None:
            st.warning("Not enough historical price data to estimate volatility for this stock.")
        else:
            equity_value = current_price * shares
            debt_value = total_debt_cr * 1e7

            st.markdown('<div class="section-label">Inputs (from live data)</div>', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                metric_card("Equity Value", f"₹{equity_value/1e7:,.0f} Cr")
            with c2:
                metric_card("Total Debt (Strike)", f"₹{debt_value/1e7:,.0f} Cr")
            with c3:
                metric_card("Equity Volatility (1Y)", f"{hist_vol*100:.1f}%")
            with c4:
                metric_card("Risk-Free Rate", f"{risk_free*100:.1f}%")

            st.markdown("<br>", unsafe_allow_html=True)
            left, right = st.columns([1, 1.4])

            with left:
                st.markdown('<div class="section-label">Merton Model — Equity as Call Option</div>', unsafe_allow_html=True)
                debt_maturity = st.slider("Debt Maturity / Time Horizon (years)", 0.5, 5.0, 1.0, 0.5, key="merton_T")
                slider_meter("Longer horizon gives asset value more time to grow above debt — usually raises implied equity", debt_maturity, 0.5, 5.0, "positive")

                if debt_value <= 0:
                    st.info(
                        f"{company_name} carries little to no debt. With strike ≈ 0, the call "
                        "option is always deep in-the-money and equity value converges to firm "
                        "value — the Merton framework adds limited insight for unleveraged "
                        "companies, but is shown below for completeness.")
                    debt_value_calc = max(debt_value, 1)
                else:
                    debt_value_calc = debt_value

                merton = merton_model(equity_value, debt_value_calc, hist_vol, risk_free, debt_maturity)

            with right:
                if merton is None:
                    st.warning("Could not compute Merton model output for this company.")
                else:
                    implied_equity_cr = merton["implied_equity"] / 1e7
                    current_equity_cr = equity_value / 1e7
                    upside_opt = ((implied_equity_cr - current_equity_cr) / current_equity_cr) * 100

                    c1, c2, c3 = st.columns(3)
                    with c1:
                        metric_card("Market Equity Value", f"₹{current_equity_cr:,.0f} Cr")
                    with c2:
                        metric_card("Option-Implied Equity", f"₹{implied_equity_cr:,.0f} Cr", "up" if upside_opt > 0 else "down")
                    with c3:
                        metric_card("Difference", f"{upside_opt:+.1f}%", "up" if upside_opt > 0 else "down")

                    vclass, vtext = verdict(upside_opt)
                    st.markdown(f'<div class="verdict-banner {vclass}">{vtext}</div>', unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)

                    st.markdown('<div class="section-label">Credit Risk View (KMV-style)</div>', unsafe_allow_html=True)
                    risk_table = pd.DataFrame({
                        "Metric": ["Implied Asset Value", "Implied Asset Volatility",
                                   "Distance to Default", "Implied Probability of Default (by T)"],
                        "Value": [
                            f"₹{merton['asset_value']/1e7:,.0f} Cr",
                            f"{merton['asset_vol']*100:.1f}%",
                            f"{merton['distance_to_default']:.2f}",
                            f"{merton['prob_default']*100:.2f}%",
                        ],
                    })
                    st.dataframe(risk_table, hide_index=True, use_container_width=True)
                    st.markdown(
                        "<p class=\"data-note\">Distance to default measures how many standard "
                        "deviations the firm's asset value sits above its debt obligations — higher "
                        "is safer. This is a simplified approximation (no iterative re-solving of "
                        "asset value/volatility) and is for illustrative purposes only.</p>",
                        unsafe_allow_html=True)

            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown('<div class="section-label">Black-Scholes Calculator</div>', unsafe_allow_html=True)
            st.markdown(
                "<p class=\"data-note\">General-purpose option pricer — defaults are pre-filled "
                "using this company's current price and estimated volatility, but can be freely "
                "adjusted to price any hypothetical option.</p>", unsafe_allow_html=True)

            bc1, bc2 = st.columns([1, 1.4])
            with bc1:
                S = st.number_input("Spot Price (₹)", value=float(current_price), min_value=0.01, key="bs_S")
                K = st.number_input("Strike Price (₹)", value=float(round(current_price * 1.05, 2)), min_value=0.01, key="bs_K")
                T_bs = st.slider("Time to Expiry (years)", 0.05, 3.0, 0.5, 0.05, key="bs_T")
                sigma_bs = st.slider("Volatility (%)", 5.0, 100.0, round(hist_vol * 100, 1), 0.5, key="bs_sigma") / 100
                r_bs = risk_free

            with bc2:
                call_price, call_delta, d1, d2 = black_scholes(S, K, T_bs, r_bs, sigma_bs, "call")
                put_price, put_delta, _, _ = black_scholes(S, K, T_bs, r_bs, sigma_bs, "put")

                cc1, cc2 = st.columns(2)
                with cc1:
                    metric_card("Call Price", f"₹{call_price:,.2f}")
                with cc2:
                    metric_card("Put Price", f"₹{put_price:,.2f}")

                st.markdown("<br>", unsafe_allow_html=True)
                bs_table = pd.DataFrame({
                    "Metric": ["d1", "d2", "Call Delta", "Put Delta"],
                    "Value": [f"{d1:.3f}", f"{d2:.3f}", f"{call_delta:.3f}", f"{put_delta:.3f}"],
                })
                st.dataframe(bs_table, hide_index=True, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<p class="data-note">Data sourced from Yahoo Finance via yfinance. '
        'Cost of equity computed via CAPM using live beta. '
        'This model is for illustrative and educational purposes only and does not constitute investment advice.</p>',
        unsafe_allow_html=True
    )
