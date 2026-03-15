import streamlit as st
import subprocess
import json
import os

st.set_page_config(page_title="Crypto Quant Radar", layout="wide")

# ----------------------------
# STYLE
# ----------------------------

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #06080d 0%, #0a0f19 100%);
        color: #f3f4f6;
    }

    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin-bottom: 0.2rem;
    }

    .subtle {
        color: #9ca3af;
        font-size: 0.95rem;
    }

    .hero {
        background:
            radial-gradient(circle at top right, rgba(34,197,94,0.12), transparent 30%),
            radial-gradient(circle at bottom left, rgba(59,130,246,0.10), transparent 35%),
            linear-gradient(135deg, #0f172a 0%, #111827 55%, #0b1220 100%);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 22px;
        padding: 1.2rem 1.25rem 1.05rem 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 30px rgba(0,0,0,0.25);
    }

    .hero-symbol {
        font-size: 1.75rem;
        font-weight: 800;
        margin-bottom: 0.15rem;
    }

    .section-title {
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 0.65rem;
    }

    .metric-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 16px;
        padding: 0.75rem 0.7rem;
        text-align: center;
        min-height: 84px;
    }

    .metric-label {
        color: #94a3b8;
        font-size: 0.78rem;
        margin-bottom: 0.18rem;
    }

    .metric-value {
        font-size: 1.08rem;
        font-weight: 800;
        color: #f8fafc;
    }

    .badge {
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 700;
        display: inline-block;
        margin-right: 6px;
        margin-top: 4px;
        border: 1px solid rgba(255,255,255,0.08);
    }

    .badge-legit {
        background: rgba(34,197,94,0.16);
        color: #4ade80;
    }

    .badge-meme {
        background: rgba(250,204,21,0.18);
        color: #fde047;
    }

    .badge-hazard {
        background: rgba(239,68,68,0.16);
        color: #f87171;
    }

    .badge-verified {
        background: rgba(59,130,246,0.18);
        color: #60a5fa;
    }

    .badge-spec {
        background: rgba(148,163,184,0.14);
        color: #cbd5e1;
    }

    .signal-pill {
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 800;
        display: inline-block;
        margin-right: 6px;
        margin-top: 4px;
    }

    .pill-pull {
        background: rgba(34,197,94,0.16);
        color: #4ade80;
    }

    .pill-watch {
        background: rgba(250,204,21,0.18);
        color: #fde047;
    }

    .pill-avoid {
        background: rgba(239,68,68,0.16);
        color: #f87171;
    }

    .pill-blue {
        background: rgba(59,130,246,0.18);
        color: #60a5fa;
    }

    .divider {
        height: 10px;
    }

    .callout {
        color: #e5e7eb;
        font-size: 0.92rem;
        line-height: 1.45;
        margin-top: 0.4rem;
    }

    .mono-box {
        background: rgba(255,255,255,0.025);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 1rem;
    }

    .row-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 16px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.7rem;
    }

    .muted {
        color: #94a3b8;
        font-size: 0.84rem;
    }

    .small-note {
        color: #94a3b8;
        font-size: 0.8rem;
        margin-top: 0.4rem;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------
# HELPERS
# ----------------------------

def run_command(cmd):
    try:
        return subprocess.check_output(cmd, text=True)
    except subprocess.CalledProcessError as e:
        return e.output
    except Exception:
        return ""

def load_json(path, default=None):
    if default is None:
        default = []
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            return default
    return default

def money_fmt(n):
    try:
        n = float(n)
    except Exception:
        return "—"

    if n >= 1_000_000_000:
        return f"${n/1_000_000_000:.2f}B"
    if n >= 1_000_000:
        return f"${n/1_000_000:.2f}M"
    if n >= 1_000:
        return f"${n/1_000:.1f}K"
    return f"${n:,.0f}"

def classify(symbol):
    coin = symbol.split("/")[0]

    LEGIT = {
        "BTC","ETH","SOL","ADA","LINK","AVAX","MATIC","ATOM",
        "FET","TAO","ALGO","XRP","BCH","LTC","DOT","ARB","OP",
        "HBAR","ICP","AAVE","CRV","RENDER","FIL","NEAR","INJ"
    }

    MEME = {
        "PEPE","DOGE","SHIB","FLOKI","BONK","TURBO","TRUMP","POPCAT",
        "PENGU","FARTCOIN","MOG","WIF"
    }

    HAZARD = {
        "A8","OPN","XAN","UP","DOWN"
    }

    VERIFIED = {
        "BTC","ETH","SOL","XRP","ADA","LINK","AVAX","HBAR","BCH","LTC"
    }

    badges = []

    if coin in VERIFIED:
        badges.append('<span class="badge badge-verified">VERIFIED</span>')

    if coin in LEGIT:
        badges.append('<span class="badge badge-legit">LEGIT</span>')
    elif coin in MEME:
        badges.append('<span class="badge badge-meme">MEME</span>')
    elif coin in HAZARD:
        badges.append('<span class="badge badge-hazard">HAZARD</span>')
    else:
        badges.append('<span class="badge badge-spec">SPEC</span>')

    return " ".join(badges)

def signal_call(score, heat, move):
    if score >= 220 or (heat >= 2.2 and move >= 5):
        return "PULL", "pill-pull"
    if score >= 100 or heat >= 1.35 or move >= 3:
        return "WATCH", "pill-watch"
    return "AVOID", "pill-avoid"

def starter_position(price, bankroll=100):
    try:
        price = float(price)
        if price <= 0:
            return "—"
        qty = bankroll / price
        return f"${bankroll} ≈ {qty:,.2f} units"
    except Exception:
        return "—"

def reason_text(coin):
    bits = []

    heat = float(coin.get("volume_heat", 0))
    move = float(coin.get("change_24h", 0))
    short = float(coin.get("short_momentum", 0))

    if heat >= 2:
        bits.append("volume is genuinely active")
    elif heat >= 1.2:
        bits.append("volume is warming up")
    else:
        bits.append("volume is not yet explosive")

    if move >= 10:
        bits.append("strong daily trend")
    elif move >= 3:
        bits.append("healthy directional move")
    elif move <= -5:
        bits.append("recent weakness, higher risk")
    else:
        bits.append("daily move is moderate")

    if short >= 1.5:
        bits.append("short-term momentum is sharp")
    elif short >= 0.5:
        bits.append("short-term momentum is building")
    else:
        bits.append("short-term momentum is mild")

    return " • ".join(bits)

# ----------------------------
# LOAD DATA
# ----------------------------

signals = load_json("signals.json", [])
trades = load_json("trade_log.json", [])
market = load_json("market_radar.json", [])
discoveries = load_json("discovery_radar.json", [])
snapshot = load_json("latest_snapshot.json", {})

market = sorted(market, key=lambda x: float(x.get("score", 0)), reverse=True)
discoveries = sorted(discoveries, key=lambda x: float(x.get("discovery_score", 0)), reverse=True)

top_market = market[0] if market else None
top_discovery = discoveries[0] if discoveries else None

agent_output = run_command(["python", "agent.py"])
stats_output = run_command(["python", "model_stats.py"])

# ----------------------------
# HEADER
# ----------------------------

left, right = st.columns([5, 1])

with left:
    st.markdown('<div class="main-title">🛸 Crypto Quant Radar</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtle">High-signal operator console for setups, discovery, heat, paper trades, and model feedback.</div>',
        unsafe_allow_html=True
    )

with right:
    if st.button("Refresh Radar", use_container_width=True):
        run_command(["python", "pipeline_runner.py"])
        st.rerun()

# top strip
strip1, strip2, strip3, strip4 = st.columns(4)
with strip1:
    st.caption(f"Last run: {snapshot.get('last_run', '—')}")
with strip2:
    st.caption(f"Top signal: {snapshot.get('top_signal', '—')}")
with strip3:
    st.caption(f"Open trades: {snapshot.get('open_trade_count', 0)}")
with strip4:
    st.caption(stats_output.split("Win Rate:")[-1].strip() if "Win Rate:" in stats_output else "Model live")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ----------------------------
# HERO
# ----------------------------

hero_left, hero_right = st.columns([1.45, 1])

with hero_left:
    if top_market:
        call, pill = signal_call(
            float(top_market.get("score", 0)),
            float(top_market.get("volume_heat", 0)),
            float(top_market.get("change_24h", 0))
        )

        st.markdown('<div class="hero">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Best Setup Right Now</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="hero-symbol">{top_market["symbol"]}</div>', unsafe_allow_html=True)
        st.markdown(classify(top_market["symbol"]), unsafe_allow_html=True)
        st.markdown(
            f'<div style="margin-top:0.45rem;"><span class="signal-pill {pill}">{call}</span></div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div class="callout">{reason_text(top_market)}</div>',
            unsafe_allow_html=True
        )

        a, b, c, d = st.columns(4)
        with a:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Price</div><div class="metric-value">${float(top_market.get("price", 0)):.6f}</div></div>',
                unsafe_allow_html=True
            )
        with b:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">24h Move</div><div class="metric-value">{float(top_market.get("change_24h", 0)):.2f}%</div></div>',
                unsafe_allow_html=True
            )
        with c:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Volume Heat</div><div class="metric-value">{float(top_market.get("volume_heat", 0)):.2f}x</div></div>',
                unsafe_allow_html=True
            )
        with d:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Starter Size</div><div class="metric-value">{starter_position(top_market.get("price", 0), 100)}</div></div>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

with hero_right:
    if top_discovery:
        st.markdown('<div class="hero">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Fresh Discovery</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="hero-symbol">{top_discovery["symbol"]}</div>', unsafe_allow_html=True)
        st.markdown(classify(top_discovery["symbol"]), unsafe_allow_html=True)
        st.markdown('<div style="margin-top:0.45rem;"><span class="signal-pill pill-watch">DISCOVERY</span></div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="callout">Discovery score is elevated. Heat is {float(top_discovery.get("volume_heat", 0)):.2f}x with short momentum at {float(top_discovery.get("short_momentum", 0)):.2f}%.</div>',
            unsafe_allow_html=True
        )

        a, b, c = st.columns(3)
        with a:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Discovery</div><div class="metric-value">{float(top_discovery.get("discovery_score", 0)):.2f}</div></div>',
                unsafe_allow_html=True
            )
        with b:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">24h Move</div><div class="metric-value">{float(top_discovery.get("change_24h", 0)):.2f}%</div></div>',
                unsafe_allow_html=True
            )
        with c:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Freshness</div><div class="metric-value">{float(top_discovery.get("freshness_bonus", top_discovery.get("freshness", 0))):.0f}</div></div>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------
# TABS
# ----------------------------

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Assistant",
    "Radar",
    "Discovery",
    "Volume Heat",
    "Trades",
    "Model"
])

# ----------------------------
# ASSISTANT
# ----------------------------

with tab1:
    st.markdown('<div class="section-title">Assistant Brief</div>', unsafe_allow_html=True)
    with st.expander("Open Brief", expanded=True):
        st.markdown('<div class="mono-box">', unsafe_allow_html=True)
        st.text(agent_output if agent_output else "No assistant brief available yet.")
        st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------
# RADAR
# ----------------------------

with tab2:
    st.markdown('<div class="section-title">Top Setups</div>', unsafe_allow_html=True)

    if not market:
        st.info("No market radar data found yet.")
    else:
        for coin in market[:8]:
            call, pill = signal_call(
                float(coin.get("score", 0)),
                float(coin.get("volume_heat", 0)),
                float(coin.get("change_24h", 0))
            )

            c1, c2, c3 = st.columns([4.2, 2.2, 1.2])

            with c1:
                st.markdown('<div class="row-card">', unsafe_allow_html=True)
                st.markdown(f"**{coin['symbol']}**")
                st.markdown(classify(coin["symbol"]), unsafe_allow_html=True)
                st.markdown(
                    f'<div style="margin-top:0.35rem;"><span class="signal-pill {pill}">{call}</span></div>',
                    unsafe_allow_html=True
                )
                st.markdown(
                    f'<div class="small-note">{reason_text(coin)}</div>',
                    unsafe_allow_html=True
                )
                st.markdown('</div>', unsafe_allow_html=True)

            with c2:
                st.markdown('<div class="row-card">', unsafe_allow_html=True)
                st.markdown(f"**Price:** ${float(coin.get('price', 0)):.6f}")
                st.markdown(f"**24h:** {float(coin.get('change_24h', 0)):.2f}%")
                st.markdown(f"**Heat:** {float(coin.get('volume_heat', 0)):.2f}x")
                st.markdown(f"**Score:** {float(coin.get('score', 0)):.2f}")
                st.markdown('</div>', unsafe_allow_html=True)

            with c3:
                st.markdown('<div class="row-card">', unsafe_allow_html=True)
                st.markdown(f"**Starter**")
                st.markdown(starter_position(coin.get("price", 0), 100))
                if st.button("Analyze", key=f"radar_{coin['symbol']}"):
                    st.session_state["selected_symbol"] = coin["symbol"]
                st.markdown('</div>', unsafe_allow_html=True)

        selected = st.session_state.get("selected_symbol")
        if selected:
            with st.expander(f"Deep analysis: {selected}", expanded=True):
                st.text(run_command(["python", "deep_scan.py", selected]))

# ----------------------------
# DISCOVERY
# ----------------------------

with tab3:
    st.markdown('<div class="section-title">Fresh Discovery</div>', unsafe_allow_html=True)

    if not discoveries:
        st.info("No discovery radar data found yet.")
    else:
        for coin in discoveries[:8]:
            if float(coin.get("discovery_score", 0)) >= 250:
                label, pill = "FRESH HOT", "pill-pull"
            elif float(coin.get("discovery_score", 0)) >= 120:
                label, pill = "WATCH", "pill-watch"
            else:
                label, pill = "EARLY", "pill-blue"

            c1, c2 = st.columns([4.2, 2.4])

            with c1:
                st.markdown('<div class="row-card">', unsafe_allow_html=True)
                st.markdown(f"**{coin['symbol']}**")
                st.markdown(classify(coin["symbol"]), unsafe_allow_html=True)
                st.markdown(
                    f'<div style="margin-top:0.35rem;"><span class="signal-pill {pill}">{label}</span></div>',
                    unsafe_allow_html=True
                )
                st.markdown(
                    f'<div class="small-note">Freshness score is elevated. Heat {float(coin.get("volume_heat", 0)):.2f}x with short momentum {float(coin.get("short_momentum", 0)):.2f}%.</div>',
                    unsafe_allow_html=True
                )
                st.markdown('</div>', unsafe_allow_html=True)

            with c2:
                st.markdown('<div class="row-card">', unsafe_allow_html=True)
                st.markdown(f"**Discovery:** {float(coin.get('discovery_score', 0)):.2f}")
                st.markdown(f"**24h:** {float(coin.get('change_24h', 0)):.2f}%")
                st.markdown(f"**Heat:** {float(coin.get('volume_heat', 0)):.2f}x")
                st.markdown(f"**Freshness:** {float(coin.get('freshness_bonus', coin.get('freshness', 0))):.0f}")
                st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------
# VOLUME HEAT
# ----------------------------

with tab4:
    st.markdown('<div class="section-title">Volume Heat</div>', unsafe_allow_html=True)

    hot = [c for c in market if float(c.get("volume_heat", 0)) >= 1.2][:8]

    if not hot:
        st.info("No meaningful volume heat right now.")
    else:
        for coin in hot:
            heat = float(coin.get("volume_heat", 0))
            if heat >= 2:
                label, pill = "HOT", "pill-pull"
            elif heat >= 1.4:
                label, pill = "WARM", "pill-watch"
            else:
                label, pill = "EARLY", "pill-blue"

            st.markdown('<div class="row-card">', unsafe_allow_html=True)
            cols = st.columns([4, 2, 2])

            with cols[0]:
                st.markdown(f"**{coin['symbol']}**")
                st.markdown(classify(coin["symbol"]), unsafe_allow_html=True)
                st.markdown(
                    f'<div style="margin-top:0.35rem;"><span class="signal-pill {pill}">{label}</span></div>',
                    unsafe_allow_html=True
                )

            with cols[1]:
                st.markdown(f"**Heat:** {heat:.2f}x")
                st.markdown(f"**24h:** {float(coin.get('change_24h', 0)):.2f}%")

            with cols[2]:
                st.markdown(f"**Price:** ${float(coin.get('price', 0)):.6f}")
                st.markdown(f"**Short:** {float(coin.get('short_momentum', 0)):.2f}%")

            st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------
# TRADES
# ----------------------------

with tab5:
    st.markdown('<div class="section-title">Paper Trades</div>', unsafe_allow_html=True)

    open_trades = [t for t in trades if t.get("status") == "OPEN"]
    closed_trades = [t for t in trades if t.get("status") != "OPEN"]

    st.markdown("#### Open")
    if not open_trades:
        st.write("No open trades.")
    else:
        for t in open_trades[-6:]:
            st.markdown('<div class="row-card">', unsafe_allow_html=True)
            cols = st.columns([3.5, 2, 2, 2])

            with cols[0]:
                st.markdown(f"**{t['symbol']}**")
                st.markdown(classify(t["symbol"]), unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f"**Entry:** {t.get('entry_price', '—')}")
            with cols[2]:
                st.markdown(f"**Size:** ${t.get('size', '—')}")
            with cols[3]:
                st.markdown(f"**Status:** {t.get('status', '—')}")

            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("#### Closed")
    if not closed_trades:
        st.write("No closed trades yet.")
    else:
        for t in closed_trades[-6:]:
            st.markdown('<div class="row-card">', unsafe_allow_html=True)
            cols = st.columns([3.5, 2, 2, 2])

            with cols[0]:
                st.markdown(f"**{t['symbol']}**")
                st.markdown(classify(t["symbol"]), unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f"**Entry:** {t.get('entry_price', '—')}")
            with cols[2]:
                st.markdown(f"**Exit:** {t.get('exit_price', '—')}")
            with cols[3]:
                st.markdown(f"**Status:** {t.get('status', '—')}")

            st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------
# MODEL
# ----------------------------

with tab6:
    st.markdown('<div class="section-title">Model Performance</div>', unsafe_allow_html=True)

    stat_cols = st.columns(4)
    stat_map = {
        "Trades": "—",
        "Wins": "—",
        "Losses": "—",
        "Status": "Live"
    }

    for line in stats_output.splitlines():
        line = line.strip()
        if "Trades:" in line and "Wins:" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 4:
                stat_map["Trades"] = parts[0].split(":")[-1].strip()
                stat_map["Wins"] = parts[1].split(":")[-1].strip()
                stat_map["Losses"] = parts[2].split(":")[-1].strip()
                stat_map["Status"] = parts[3].split(":")[-1].strip()

    labels = list(stat_map.keys())
    for i, label in enumerate(labels):
        with stat_cols[i]:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{stat_map[label]}</div></div>',
                unsafe_allow_html=True
            )

    with st.expander("Raw model output"):
        st.markdown('<div class="mono-box">', unsafe_allow_html=True)
        st.text(stats_output if stats_output else "No model stats available.")
        st.markdown('</div>', unsafe_allow_html=True)