import streamlit as st
import subprocess
import json
import os
from datetime import datetime

st.set_page_config(page_title="Crypto Quant Radar", layout="wide", initial_sidebar_state="collapsed")

# ----------------------------
# STYLE — Apple-grade dark UI
# ----------------------------

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,400&display=swap');

    * { box-sizing: border-box; }

    .stApp {
        background: #050709;
        color: #f3f4f6;
    }

    /* Kill Streamlit chrome noise */
    header[data-testid="stHeader"],
    .stDeployButton,
    footer { display: none !important; }

    section[data-testid="stSidebar"] { display: none !important; }

    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display",
                     "SF Pro Text", "Helvetica Neue", sans-serif;
    }

    /* ---- LAYOUT ---- */

    .main-title {
        font-size: 2.1rem;
        font-weight: 700;
        letter-spacing: -0.045em;
        color: #f9fafb;
        line-height: 1;
        margin-bottom: 0.2rem;
    }

    .sub-title {
        font-size: 0.94rem;
        color: #525968;
        letter-spacing: 0.01em;
        font-weight: 400;
    }

    .status-row {
        display: flex;
        gap: 1.6rem;
        margin-top: 0.6rem;
        flex-wrap: wrap;
    }

    .status-item {
        font-size: 0.86rem;
        color: #3f4755;
        display: flex;
        align-items: center;
        gap: 5px;
    }

    .status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #22c55e;
        display: inline-block;
        box-shadow: 0 0 6px rgba(34,197,94,0.7);
        animation: pulse-dot 2.4s ease-in-out infinite;
    }

    @keyframes pulse-dot {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
    }

    /* ---- CARDS ---- */

    .glass {
        background: rgba(255,255,255,0.028);
        border: 1px solid rgba(255,255,255,0.065);
        border-radius: 20px;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
    }

    .hero-card {
        background:
            radial-gradient(ellipse 80% 60% at 90% 10%, rgba(34,197,94,0.07), transparent),
            radial-gradient(ellipse 60% 50% at 10% 90%, rgba(59,130,246,0.06), transparent),
            rgba(255,255,255,0.018);
        border: 1px solid rgba(255,255,255,0.065);
        border-radius: 22px;
        padding: 1.35rem 1.4rem 1.2rem;
        backdrop-filter: blur(24px);
        position: relative;
        overflow: hidden;
    }

    .hero-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.12), transparent);
    }

    /* ---- TYPOGRAPHY ---- */

    .hero-symbol {
        font-size: 2.15rem;
        font-weight: 700;
        letter-spacing: -0.04em;
        color: #f8fafc;
        line-height: 1;
        margin-bottom: 0.5rem;
    }

    .section-label {
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #3d4452;
        margin-bottom: 0.75rem;
    }

    .callout {
        font-size: 1.0rem;
        color: #9ca3af;
        line-height: 1.6;
        margin-top: 0.55rem;
        font-weight: 400;
    }

    /* ---- METRICS ---- */

    .metric-block {
        background: rgba(255,255,255,0.022);
        border: 1px solid rgba(255,255,255,0.055);
        border-radius: 14px;
        padding: 0.75rem 0.7rem;
        text-align: center;
    }

    .metric-label {
        font-size: 0.8rem;
        color: #4b5563;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 0.35rem;
        font-weight: 500;
    }

    .metric-value {
        font-size: 1.18rem;
        font-weight: 650;
        color: #e9ecf0;
        line-height: 1;
    }

    /* ---- BADGES ---- */

    .tag {
        padding: 3px 9px;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        display: inline-block;
        margin-right: 5px;
        margin-top: 3px;
        text-transform: uppercase;
    }

    .tag-legit   { background: rgba(34,197,94,0.12);  color: #4ade80; border: 1px solid rgba(34,197,94,0.2);   }
    .tag-meme    { background: rgba(250,204,21,0.12);  color: #fde047; border: 1px solid rgba(250,204,21,0.2);  }
    .tag-hazard  { background: rgba(239,68,68,0.12);   color: #f87171; border: 1px solid rgba(239,68,68,0.2);   }
    .tag-verified{ background: rgba(59,130,246,0.12);  color: #60a5fa; border: 1px solid rgba(59,130,246,0.2);  }
    .tag-spec    { background: rgba(148,163,184,0.08); color: #94a3b8; border: 1px solid rgba(148,163,184,0.15);}

    /* ---- SIGNAL PILLS ---- */

    .pill {
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 800;
        letter-spacing: 0.07em;
        display: inline-block;
        margin-right: 5px;
        text-transform: uppercase;
    }

    .pill-pull { background: rgba(34,197,94,0.14);  color: #4ade80; }
    .pill-watch{ background: rgba(250,204,21,0.14);  color: #fde047; }
    .pill-avoid{ background: rgba(239,68,68,0.14);   color: #f87171; }
    .pill-blue { background: rgba(59,130,246,0.14);  color: #60a5fa; }

    /* ---- ROW CARDS ---- */

    .row-card {
        background: rgba(255,255,255,0.022);
        border: 1px solid rgba(255,255,255,0.055);
        border-radius: 16px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.6rem;
        transition: border-color 0.2s;
    }

    .row-card:hover {
        border-color: rgba(255,255,255,0.1);
    }

    .row-symbol {
        font-size: 1.12rem;
        font-weight: 650;
        color: #eef2ff;
        letter-spacing: -0.02em;
    }

    .row-meta {
        font-size: 0.92rem;
        color: #6b7280;
        margin-top: 0.25rem;
        line-height: 1.5;
    }

    /* ---- ASSISTANT BRIEF ---- */

    .brief-container {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.065);
        border-radius: 22px;
        padding: 1.5rem 1.6rem;
        position: relative;
        overflow: hidden;
    }

    .brief-container::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
    }

    .brief-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 1.2rem;
        padding-bottom: 0.85rem;
        border-bottom: 1px solid rgba(255,255,255,0.055);
    }

    .brief-icon {
        width: 32px;
        height: 32px;
        border-radius: 10px;
        background: linear-gradient(135deg, rgba(99,102,241,0.35), rgba(59,130,246,0.25));
        border: 1px solid rgba(99,102,241,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        flex-shrink: 0;
    }

    .brief-title-text {
        font-size: 1.0rem;
        font-weight: 600;
        color: #c7d0e0;
        letter-spacing: -0.01em;
    }

    .brief-timestamp {
        font-size: 0.84rem;
        color: #3a404f;
        margin-left: auto;
        font-family: 'DM Mono', monospace;
    }

    /* ---- VITAL ROWS ---- */

    .vital-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 0.6rem;
        margin-bottom: 1.1rem;
    }

    .vital-cell {
        background: rgba(255,255,255,0.018);
        border: 1px solid rgba(255,255,255,0.048);
        border-radius: 12px;
        padding: 0.7rem 0.85rem;
    }

    .vital-key {
        font-size: 0.79rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #3d4452;
        margin-bottom: 0.3rem;
    }

    .vital-val {
        font-size: 1.02rem;
        font-weight: 650;
        color: #dde2ec;
        letter-spacing: -0.01em;
    }

    .vital-val.green  { color: #4ade80; }
    .vital-val.yellow { color: #fde047; }
    .vital-val.red    { color: #f87171; }
    .vital-val.blue   { color: #60a5fa; }

    /* ---- BRIEF TEXT BLOCKS ---- */

    .brief-block {
        background: rgba(255,255,255,0.015);
        border-left: 2px solid rgba(99,102,241,0.35);
        border-radius: 0 10px 10px 0;
        padding: 0.75rem 0.95rem;
        margin-bottom: 0.65rem;
    }

    .brief-block-label {
        font-size: 0.79rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #6366f1;
        margin-bottom: 0.35rem;
    }

    .brief-block-text {
        font-size: 1.0rem;
        color: #9ca3af;
        line-height: 1.65;
        font-weight: 400;
    }

    /* ---- ALERT BLOCKS ---- */

    .alert-block {
        display: flex;
        gap: 0.75rem;
        align-items: flex-start;
        padding: 0.8rem 0.95rem;
        border-radius: 14px;
        margin-bottom: 0.6rem;
        font-size: 0.98rem;
        line-height: 1.55;
        color: #d1d5db;
    }

    .alert-green  { background: rgba(34,197,94,0.07);  border: 1px solid rgba(34,197,94,0.15);  }
    .alert-yellow { background: rgba(250,204,21,0.07);  border: 1px solid rgba(250,204,21,0.15);  }
    .alert-red    { background: rgba(239,68,68,0.07);   border: 1px solid rgba(239,68,68,0.15);   }
    .alert-blue   { background: rgba(59,130,246,0.07);  border: 1px solid rgba(59,130,246,0.15);  }
    .alert-purple { background: rgba(99,102,241,0.07);  border: 1px solid rgba(99,102,241,0.15);  }

    .alert-icon {
        font-size: 1.05rem;
        flex-shrink: 0;
        margin-top: 1px;
    }

    /* ---- RAW FALLBACK ---- */

    .brief-raw {
        font-family: 'DM Mono', monospace;
        font-size: 0.94rem;
        color: #6b7280;
        line-height: 1.8;
        white-space: pre-wrap;
        word-break: break-word;
    }

    /* ---- MISC ---- */

    .mono-label {
        font-family: 'DM Mono', monospace;
        font-size: 0.87rem;
        color: #4b5563;
    }

    .divider { height: 14px; }

    .small-note {
        font-size: 0.9rem;
        color: #4b5563;
        margin-top: 0.3rem;
        line-height: 1.5;
    }

    /* Streamlit tab overrides */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 6px 16px;
        font-size: 0.92rem;
        font-weight: 500;
        color: #525968;
        background: transparent;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(255,255,255,0.06) !important;
        color: #e5e7eb !important;
    }

    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }

    /* Button */
    .stButton > button {
        background: rgba(255,255,255,0.055);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 12px;
        color: #c9d1df;
        font-size: 0.92rem;
        font-weight: 500;
        padding: 8px 18px;
        transition: all 0.2s;
    }

    .stButton > button:hover {
        background: rgba(255,255,255,0.085);
        border-color: rgba(255,255,255,0.14);
        color: #f0f2f5;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------
# HELPERS
# ----------------------------

def run_command(cmd):
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        return e.output or ""
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

def classify(symbol):
    coin = symbol.split("/")[0]
    LEGIT    = {"BTC","ETH","SOL","ADA","LINK","AVAX","MATIC","ATOM","FET","TAO","ALGO","XRP","BCH","LTC","DOT","ARB","OP","HBAR","ICP","AAVE","CRV","RENDER","FIL","NEAR","INJ","UNI","DOGE"}
    MEME     = {"PEPE","DOGE","SHIB","FLOKI","BONK","TRUMP","POPCAT","PENGU","FARTCOIN","MOG","WIF","USELESS"}
    HAZARD   = {"A8","OPN","XAN","UP","DOWN"}
    VERIFIED = {"BTC","ETH","SOL","XRP","ADA","LINK","AVAX","HBAR","BCH","LTC","UNI","DOGE"}

    badges = []
    if coin in VERIFIED:
        badges.append('<span class="tag tag-verified">Verified</span>')
    if coin in LEGIT:
        badges.append('<span class="tag tag-legit">Legit</span>')
    elif coin in MEME:
        badges.append('<span class="tag tag-meme">Meme</span>')
    elif coin in HAZARD:
        badges.append('<span class="tag tag-hazard">Hazard</span>')
    else:
        badges.append('<span class="tag tag-spec">Spec</span>')
    return " ".join(badges)

def signal_call(score, heat, move):
    if score >= 220 or (heat >= 2.2 and move >= 5):
        return "Pull", "pill-pull"
    if score >= 100 or heat >= 1.35 or move >= 3:
        return "Watch", "pill-watch"
    return "Avoid", "pill-avoid"

def starter_position(price, bankroll=100):
    try:
        price = float(price)
        if price <= 0:
            return "—"
        qty = bankroll / price
        return f"${bankroll} → {qty:,.2f} units"
    except Exception:
        return "—"

def reason_text(coin):
    bits = []
    heat  = float(coin.get("volume_heat", 0))
    move  = float(coin.get("change_24h", 0))
    short = float(coin.get("short_momentum", 0))
    if heat >= 2:      bits.append("Volume explosive")
    elif heat >= 1.2:  bits.append("Volume warming")
    else:              bits.append("Volume quiet")
    if move >= 10:     bits.append("strong daily trend")
    elif move >= 3:    bits.append("healthy move")
    elif move <= -5:   bits.append("recent weakness")
    else:              bits.append("moderate move")
    if short >= 1.5:   bits.append("sharp short-term momentum")
    elif short >= 0.5: bits.append("momentum building")
    else:              bits.append("momentum mild")
    return " · ".join(bits)


# ----------------------------
# AGENT OUTPUT PARSER
# Cleanly extracts structured fields or falls back to raw text.
# ----------------------------

def parse_agent_output(raw: str):
    """
    Returns a dict with keys:
      summary, top_pick, top_pick_reason, signals (list of dicts),
      risk_note, market_read, raw
    Falls back gracefully if agent output is unstructured.
    """
    result = {
        "summary": "",
        "top_pick": "",
        "top_pick_reason": "",
        "signals": [],
        "risk_note": "",
        "market_read": "",
        "raw": "",
    }

    if not raw or not raw.strip():
        return result

    lines = [l.strip() for l in raw.splitlines()]
    cleaned = []

    for line in lines:
        # Drop internal agent markers
        if line.startswith("AGENT_") or line.startswith("DEBUG_") or line.startswith("INFO_"):
            continue
        if not line:
            continue
        cleaned.append(line)

    result["raw"] = "\n".join(cleaned)

    # Try to parse key: value style from agent output
    import re
    full_text = result["raw"]

    def extract(pattern, text, group=1, default=""):
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return m.group(group).strip() if m else default

    result["summary"]         = extract(r"(?:SUMMARY|OVERVIEW|BRIEF)[:\s]+(.+?)(?=\n[A-Z_]+:|$)", full_text)
    result["top_pick"]        = extract(r"(?:TOP[_ ]PICK|BEST[_ ]SETUP|LEAD)[:\s]+([A-Z0-9/]+)", full_text)
    result["top_pick_reason"] = extract(r"(?:REASON|RATIONALE|WHY)[:\s]+(.+?)(?=\n[A-Z_]+:|$)", full_text)
    result["risk_note"]       = extract(r"(?:RISK|CAUTION|WARNING)[:\s]+(.+?)(?=\n[A-Z_]+:|$)", full_text)
    result["market_read"]     = extract(r"(?:MARKET[_ ]READ|MACRO|CONTEXT)[:\s]+(.+?)(?=\n[A-Z_]+:|$)", full_text)

    # Parse signal lines: e.g. "SIGNAL: BTC/USDT | PULL | Heat 2.3x | +5.2%"
    for line in cleaned:
        sig_match = re.match(
            r"SIGNAL[:\s]+([A-Z0-9/]+)\s*[|\-]\s*([A-Z]+)\s*[|\-]?\s*(.*)",
            line, re.IGNORECASE
        )
        if sig_match:
            result["signals"].append({
                "symbol": sig_match.group(1).strip(),
                "call":   sig_match.group(2).strip(),
                "note":   sig_match.group(3).strip(),
            })

    return result


def render_brief(parsed: dict, snapshot: dict, market: list):
    """Render the assistant brief panel using direct st.markdown calls — never string-built HTML."""
    import re

    now_str    = datetime.now().strftime("%H:%M · %b %d")
    top        = market[0] if market else {}
    top_signal = snapshot.get("top_signal", top.get("symbol", "—"))
    open_trades = snapshot.get("open_trade_count", 0)
    heat       = float(top.get("volume_heat", 0))
    move       = float(top.get("change_24h", 0))
    score      = float(top.get("score", 0))

    mood     = "🟢 Risk On"  if move > 3  else ("🟡 Neutral" if move > -2 else "🔴 Risk Off")
    mood_cls = "green"       if move > 3  else ("yellow"     if move > -2 else "red")
    heat_cls = "green"       if heat >= 2 else ("yellow"     if heat >= 1.2 else "")
    move_cls = "green"       if move > 0  else "red"

    # ── Container open + header ───────────────────────────────────────────
    st.markdown(f"""
    <div class="brief-container">
      <div class="brief-header">
        <div class="brief-icon">✦</div>
        <div class="brief-title-text">Assistant Brief</div>
        <div class="brief-timestamp">{now_str}</div>
      </div>
      <div class="vital-grid">
        <div class="vital-cell">
          <div class="vital-key">Top Signal</div>
          <div class="vital-val blue">{top_signal}</div>
        </div>
        <div class="vital-cell">
          <div class="vital-key">Market Mood</div>
          <div class="vital-val {mood_cls}">{mood}</div>
        </div>
        <div class="vital-cell">
          <div class="vital-key">Volume Heat</div>
          <div class="vital-val {heat_cls}">{heat:.2f}×</div>
        </div>
        <div class="vital-cell">
          <div class="vital-key">24h Move</div>
          <div class="vital-val {move_cls}">{move:+.2f}%</div>
        </div>
        <div class="vital-cell">
          <div class="vital-key">Quant Score</div>
          <div class="vital-val">{score:.0f}</div>
        </div>
        <div class="vital-cell">
          <div class="vital-key">Open Trades</div>
          <div class="vital-val">{open_trades}</div>
        </div>
      </div>
    """, unsafe_allow_html=True)

    # ── Brief content blocks ──────────────────────────────────────────────
    has_structured = any([
        parsed["summary"], parsed["top_pick_reason"],
        parsed["market_read"], parsed["risk_note"], parsed["signals"]
    ])

    if has_structured:
        if parsed["summary"]:
            st.markdown(f"""
            <div class="brief-block">
              <div class="brief-block-label">Overview</div>
              <div class="brief-block-text">{parsed['summary']}</div>
            </div>""", unsafe_allow_html=True)

        if parsed["market_read"]:
            st.markdown(f"""
            <div class="brief-block">
              <div class="brief-block-label">Market Context</div>
              <div class="brief-block-text">{parsed['market_read']}</div>
            </div>""", unsafe_allow_html=True)

        if parsed["top_pick"] and parsed["top_pick_reason"]:
            st.markdown(f"""
            <div class="alert-block alert-green">
              <div class="alert-icon">◉</div>
              <div><strong style="color:#4ade80;">{parsed['top_pick']}</strong> — {parsed['top_pick_reason']}</div>
            </div>""", unsafe_allow_html=True)
        elif parsed["top_pick"]:
            st.markdown(f"""
            <div class="alert-block alert-green">
              <div class="alert-icon">◉</div>
              <div>Lead pick: <strong style="color:#4ade80;">{parsed['top_pick']}</strong></div>
            </div>""", unsafe_allow_html=True)

        for sig in parsed["signals"][:5]:
            call_lower = sig["call"].lower()
            if "pull" in call_lower:
                color_cls, icon = "alert-green", "▲"
            elif "watch" in call_lower:
                color_cls, icon = "alert-yellow", "◎"
            else:
                color_cls, icon = "alert-red", "▽"
            pill_cls = f"pill-{call_lower[:4]}"
            st.markdown(f"""
            <div class="alert-block {color_cls}">
              <div class="alert-icon">{icon}</div>
              <div><strong>{sig['symbol']}</strong>&nbsp;
                <span class="pill {pill_cls}">{sig['call']}</span>&nbsp;
                {sig['note']}
              </div>
            </div>""", unsafe_allow_html=True)

        if parsed["risk_note"]:
            st.markdown(f"""
            <div class="alert-block alert-yellow">
              <div class="alert-icon">⚠</div>
              <div>{parsed['risk_note']}</div>
            </div>""", unsafe_allow_html=True)

    else:
        raw = parsed["raw"]
        if raw:
            alert_patterns = [
                (r"\bpull\b",  "alert-green",  "▲"),
                (r"\bwatch\b", "alert-yellow", "◎"),
                (r"\bavoid\b", "alert-red",    "▽"),
                (r"\brisk\b",  "alert-yellow", "⚠"),
                (r"\bhot\b",   "alert-green",  "◉"),
            ]
            paragraphs = [p.strip() for p in re.split(r'\n{2,}', raw) if p.strip()]
            for para in paragraphs:
                matched = False
                for pattern, cls, icon in alert_patterns:
                    if re.search(pattern, para, re.IGNORECASE):
                        st.markdown(f"""
                        <div class="alert-block {cls}">
                          <div class="alert-icon">{icon}</div>
                          <div>{para}</div>
                        </div>""", unsafe_allow_html=True)
                        matched = True
                        break
                if not matched:
                    st.markdown(f"""
                    <div class="brief-block">
                      <div class="brief-block-text">{para}</div>
                    </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="brief-block">
              <div class="brief-block-label">Status</div>
              <div class="brief-block-text" style="color:#3a404f;">
                No agent output yet. Hit ↺&nbsp;Refresh to run the pipeline.
              </div>
            </div>""", unsafe_allow_html=True)

    # ── Container close ───────────────────────────────────────────────────
    st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------
# LOAD DATA
# ----------------------------

signals     = load_json("signals.json", [])
trades      = load_json("trade_log.json", [])
market      = load_json("market_radar.json", [])
discoveries = load_json("discovery_radar.json", [])
snapshot    = load_json("latest_snapshot.json", {})

market      = sorted(market,      key=lambda x: float(x.get("score", 0)),           reverse=True)
discoveries = sorted(discoveries, key=lambda x: float(x.get("discovery_score", 0)), reverse=True)

top_market    = market[0]      if market      else None
top_discovery = discoveries[0] if discoveries else None

agent_output  = run_command(["python", "agent.py"])
agent_parsed  = parse_agent_output(agent_output)
stats_output  = run_command(["python", "model_stats.py"])

# ----------------------------
# HEADER
# ----------------------------

left, right = st.columns([5, 1])

with left:
    st.markdown('<div class="main-title">Crypto Quant Radar</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">High-signal operator console · setups · discovery · heat · trades · model</div>', unsafe_allow_html=True)
    last_run_str = snapshot.get("last_run", "—")
    top_sig_str  = snapshot.get("top_signal", top_market["symbol"] if top_market else "—")
    open_count   = snapshot.get("open_trade_count", 0)
    st.markdown(f"""
    <div class="status-row">
      <div class="status-item"><span class="status-dot"></span>Live</div>
      <div class="status-item mono-label">Last run: {last_run_str}</div>
      <div class="status-item mono-label">Top: {top_sig_str}</div>
      <div class="status-item mono-label">Open trades: {open_count}</div>
    </div>""", unsafe_allow_html=True)

with right:
    if st.button("↺  Refresh", use_container_width=True):
        with st.spinner("Running pipeline…"):
            # Try pipeline_runner first, fall back to running scanners directly
            pipeline_out = ""
            try:
                pipeline_out = subprocess.check_output(
                    ["python", "pipeline_runner.py"],
                    text=True, stderr=subprocess.STDOUT, timeout=60
                )
            except subprocess.CalledProcessError as e:
                pipeline_out = e.output or ""
            except FileNotFoundError:
                # pipeline_runner.py doesn't exist — run individual scripts
                for script in ["scanner.py", "discovery.py", "agent.py"]:
                    if os.path.exists(script):
                        try:
                            subprocess.run(["python", script], timeout=30,
                                           capture_output=True)
                        except Exception:
                            pass
            except Exception:
                pass

            # Always try to refresh agent output
            if os.path.exists("agent.py"):
                try:
                    subprocess.run(["python", "agent.py"], timeout=30,
                                   capture_output=True)
                except Exception:
                    pass
        st.rerun()

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ----------------------------
# HERO CARDS
# ----------------------------

hero_left, hero_right = st.columns([1.45, 1])

with hero_left:
    if top_market:
        call, pill = signal_call(
            float(top_market.get("score", 0)),
            float(top_market.get("volume_heat", 0)),
            float(top_market.get("change_24h", 0))
        )
        st.markdown('<div class="hero-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Best Setup Right Now</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="hero-symbol">{top_market["symbol"]}</div>', unsafe_allow_html=True)
        st.markdown(classify(top_market["symbol"]), unsafe_allow_html=True)
        st.markdown(f'<div style="margin-top:0.5rem;"><span class="pill {pill}">{call}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="callout">{reason_text(top_market)}</div>', unsafe_allow_html=True)

        a, b, c, d = st.columns(4)
        def metric(label, val):
            return f'<div class="metric-block"><div class="metric-label">{label}</div><div class="metric-value">{val}</div></div>'

        with a: st.markdown(metric("Price", f"${float(top_market.get('price',0)):.6f}"), unsafe_allow_html=True)
        with b: st.markdown(metric("24h", f"{float(top_market.get('change_24h',0)):+.2f}%"), unsafe_allow_html=True)
        with c: st.markdown(metric("Heat", f"{float(top_market.get('volume_heat',0)):.2f}×"), unsafe_allow_html=True)
        with d: st.markdown(metric("Starter", starter_position(top_market.get("price",0))), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

with hero_right:
    if top_discovery:
        st.markdown('<div class="hero-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Fresh Discovery</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="hero-symbol">{top_discovery["symbol"]}</div>', unsafe_allow_html=True)
        st.markdown(classify(top_discovery["symbol"]), unsafe_allow_html=True)
        st.markdown('<div style="margin-top:0.5rem;"><span class="pill pill-blue">Discovery</span></div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="callout">Heat {float(top_discovery.get("volume_heat",0)):.2f}× · Short momentum {float(top_discovery.get("short_momentum",0)):.2f}% · Discovery score elevated</div>',
            unsafe_allow_html=True
        )
        a, b, c = st.columns(3)
        def metric(label, val):
            return f'<div class="metric-block"><div class="metric-label">{label}</div><div class="metric-value">{val}</div></div>'
        with a: st.markdown(metric("Score", f"{float(top_discovery.get('discovery_score',0)):.2f}"), unsafe_allow_html=True)
        with b: st.markdown(metric("24h", f"{float(top_discovery.get('change_24h',0)):+.2f}%"), unsafe_allow_html=True)
        with c: st.markdown(metric("Freshness", f"{float(top_discovery.get('freshness_bonus', top_discovery.get('freshness',0))):.0f}"), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------
# MOONSHOT STRIP
# ----------------------------

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

if top_market:
    m1, m2, m3 = st.columns([1, 1, 3])
    def metric(label, val):
        return f'<div class="metric-block"><div class="metric-label">{label}</div><div class="metric-value">{val}</div></div>'
    with m1: st.markdown(metric("Moonshot Mode",  top_market.get("moonshot_bias", "—")), unsafe_allow_html=True)
    with m2: st.markdown(metric("Quality Tier",   top_market.get("quality_tier",  "—")), unsafe_allow_html=True)
    with m3: st.markdown(metric("Setup Read",      top_market.get("setup_note", "No setup note yet.")), unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ----------------------------
# TABS
# ----------------------------

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Assistant", "Radar", "Discovery", "Volume Heat", "Trades", "Model"
])

# ----------------------------
# ASSISTANT
# ----------------------------

with tab1:
    render_brief(agent_parsed, snapshot, market)

    if agent_parsed["raw"]:
        with st.expander("Raw agent output", expanded=False):
            st.code(agent_parsed["raw"], language=None)

# ----------------------------
# RADAR
# ----------------------------

with tab2:
    st.markdown('<div class="section-label">Top Setups</div>', unsafe_allow_html=True)

    if not market:
        st.info("No market radar data found yet.")
    else:
        for coin in market[:8]:
            call, pill = signal_call(
                float(coin.get("score", 0)),
                float(coin.get("volume_heat", 0)),
                float(coin.get("change_24h", 0))
            )
            c1, c2, c3 = st.columns([4.2, 2.2, 1.4])
            with c1:
                st.markdown('<div class="row-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="row-symbol">{coin["symbol"]}</div>', unsafe_allow_html=True)
                st.markdown(classify(coin["symbol"]), unsafe_allow_html=True)
                st.markdown(f'<div style="margin-top:0.4rem"><span class="pill {pill}">{call}</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="small-note">{reason_text(coin)}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="row-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="row-meta">Price &nbsp; <strong style="color:#dde2ec;">${float(coin.get("price",0)):.6f}</strong></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="row-meta">24h &nbsp;&nbsp;&nbsp; <strong style="color:{"#4ade80" if float(coin.get("change_24h",0)) > 0 else "#f87171"}">{float(coin.get("change_24h",0)):+.2f}%</strong></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="row-meta">Heat &nbsp;&nbsp; <strong style="color:#dde2ec;">{float(coin.get("volume_heat",0)):.2f}×</strong></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="row-meta">Score &nbsp; <strong style="color:#dde2ec;">{float(coin.get("score",0)):.1f}</strong></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with c3:
                st.markdown('<div class="row-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="row-meta" style="font-size:0.74rem;color:#3d4452;margin-bottom:0.35rem;">STARTER</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="row-meta" style="font-size:0.8rem;color:#9ca3af;">{starter_position(coin.get("price",0))}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------
# DISCOVERY
# ----------------------------

with tab3:
    st.markdown('<div class="section-label">Fresh Discovery</div>', unsafe_allow_html=True)

    if not discoveries:
        st.info("No discovery radar data found yet.")
    else:
        for coin in discoveries[:8]:
            ds = float(coin.get("discovery_score", 0))
            if ds >= 250:   label, pill = "Fresh Hot",  "pill-pull"
            elif ds >= 120: label, pill = "Watch",       "pill-watch"
            else:           label, pill = "Early",       "pill-blue"

            c1, c2 = st.columns([4.2, 2.4])
            with c1:
                st.markdown('<div class="row-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="row-symbol">{coin["symbol"]}</div>', unsafe_allow_html=True)
                st.markdown(classify(coin["symbol"]), unsafe_allow_html=True)
                st.markdown(f'<div style="margin-top:0.4rem"><span class="pill {pill}">{label}</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="small-note">Heat {float(coin.get("volume_heat",0)):.2f}× · Short momentum {float(coin.get("short_momentum",0)):.2f}%</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="row-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="row-meta">Discovery &nbsp; <strong style="color:#dde2ec;">{ds:.2f}</strong></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="row-meta">24h &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <strong style="color:{"#4ade80" if float(coin.get("change_24h",0)) > 0 else "#f87171"}">{float(coin.get("change_24h",0)):+.2f}%</strong></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="row-meta">Heat &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <strong style="color:#dde2ec;">{float(coin.get("volume_heat",0)):.2f}×</strong></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="row-meta">Freshness &nbsp; <strong style="color:#dde2ec;">{float(coin.get("freshness_bonus", coin.get("freshness",0))):.0f}</strong></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------
# VOLUME HEAT
# ----------------------------

with tab4:
    st.markdown('<div class="section-label">Volume Heat</div>', unsafe_allow_html=True)
    hot = [c for c in market if float(c.get("volume_heat", 0)) >= 1.2][:8]

    if not hot:
        st.info("No meaningful volume heat right now.")
    else:
        for coin in hot:
            heat = float(coin.get("volume_heat", 0))
            if heat >= 2:    label, pill = "Hot",   "pill-pull"
            elif heat >= 1.4: label, pill = "Warm",  "pill-watch"
            else:             label, pill = "Early", "pill-blue"

            st.markdown('<div class="row-card">', unsafe_allow_html=True)
            cols = st.columns([4, 2, 2])
            with cols[0]:
                st.markdown(f'<div class="row-symbol">{coin["symbol"]}</div>', unsafe_allow_html=True)
                st.markdown(classify(coin["symbol"]), unsafe_allow_html=True)
                st.markdown(f'<div style="margin-top:0.4rem"><span class="pill {pill}">{label}</span></div>', unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f'<div class="row-meta">Heat &nbsp; <strong style="color:#dde2ec;">{heat:.2f}×</strong></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="row-meta">24h &nbsp;&nbsp; <strong style="color:{"#4ade80" if float(coin.get("change_24h",0)) > 0 else "#f87171"}">{float(coin.get("change_24h",0)):+.2f}%</strong></div>', unsafe_allow_html=True)
            with cols[2]:
                st.markdown(f'<div class="row-meta">Price &nbsp; <strong style="color:#dde2ec;">${float(coin.get("price",0)):.6f}</strong></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="row-meta">Short &nbsp; <strong style="color:#dde2ec;">{float(coin.get("short_momentum",0)):.2f}%</strong></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------
# TRADES
# ----------------------------

with tab5:
    st.markdown('<div class="section-label">Paper Trades</div>', unsafe_allow_html=True)

    open_trades   = [t for t in trades if t.get("status") == "OPEN"]
    closed_trades = [t for t in trades if t.get("status") != "OPEN"]

    st.markdown("#### Open")
    if not open_trades:
        st.markdown('<div class="row-meta" style="padding:0.5rem 0;color:#3d4452;">No open trades.</div>', unsafe_allow_html=True)
    else:
        for t in open_trades[-6:]:
            st.markdown('<div class="row-card">', unsafe_allow_html=True)
            cols = st.columns([3.5, 2, 2, 2])
            with cols[0]:
                st.markdown(f'<div class="row-symbol">{t["symbol"]}</div>', unsafe_allow_html=True)
                st.markdown(classify(t["symbol"]), unsafe_allow_html=True)
            with cols[1]: st.markdown(f'<div class="row-meta">Entry &nbsp; <strong style="color:#dde2ec;">{t.get("entry_price","—")}</strong></div>', unsafe_allow_html=True)
            with cols[2]: st.markdown(f'<div class="row-meta">Size &nbsp;&nbsp; <strong style="color:#dde2ec;">${t.get("size","—")}</strong></div>', unsafe_allow_html=True)
            with cols[3]: st.markdown(f'<div class="row-meta">Status &nbsp; <span class="pill pill-blue">{t.get("status","—")}</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("#### Closed")
    if not closed_trades:
        st.markdown('<div class="row-meta" style="padding:0.5rem 0;color:#3d4452;">No closed trades yet.</div>', unsafe_allow_html=True)
    else:
        for t in closed_trades[-6:]:
            status = t.get("status", "—")
            spill  = "pill-pull" if status == "WIN" else "pill-avoid" if status == "LOSS" else "pill-blue"
            st.markdown('<div class="row-card">', unsafe_allow_html=True)
            cols = st.columns([3.5, 2, 2, 2])
            with cols[0]:
                st.markdown(f'<div class="row-symbol">{t["symbol"]}</div>', unsafe_allow_html=True)
                st.markdown(classify(t["symbol"]), unsafe_allow_html=True)
            with cols[1]: st.markdown(f'<div class="row-meta">Entry &nbsp; <strong style="color:#dde2ec;">{t.get("entry_price","—")}</strong></div>', unsafe_allow_html=True)
            with cols[2]: st.markdown(f'<div class="row-meta">Exit &nbsp;&nbsp; <strong style="color:#dde2ec;">{t.get("exit_price","—")}</strong></div>', unsafe_allow_html=True)
            with cols[3]: st.markdown(f'<div class="row-meta"><span class="pill {spill}">{status}</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------
# MODEL
# ----------------------------

with tab6:
    st.markdown('<div class="section-label">Model Performance</div>', unsafe_allow_html=True)

    wins       = len([t for t in trades if t.get("status") == "WIN"])
    losses     = len([t for t in trades if t.get("status") == "LOSS"])
    total      = wins + losses
    open_count = len([t for t in trades if t.get("status") == "OPEN"])
    winrate    = f"{wins/total*100:.1f}%" if total > 0 else "—"

    stat_cols = st.columns(5)
    for col, (lbl, val) in zip(stat_cols, [
        ("Trades",   total),
        ("Wins",     wins),
        ("Losses",   losses),
        ("Open",     open_count),
        ("Win Rate", winrate),
    ]):
        with col:
            st.markdown(
                f'<div class="metric-block"><div class="metric-label">{lbl}</div><div class="metric-value">{val}</div></div>',
                unsafe_allow_html=True
            )

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    with st.expander("Raw model output", expanded=False):
        st.markdown(
            f'<div class="brief-raw">{stats_output if stats_output else "No model stats available."}</div>',
            unsafe_allow_html=True
        )