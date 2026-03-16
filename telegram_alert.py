import json
import os
import urllib.request
import urllib.parse
import urllib.error

# ----------------------------
# CONFIG — replace token after exposing it
# ----------------------------

BOT_TOKEN = "8522948500:AAETGGT4JIsgvTpkNSviBttDUU3b-ZZveso"
CHAT_ID   = "5115148555"

MARKET_FILE    = "market_radar.json"
DISCOVERY_FILE = "discovery_radar.json"
TRADES_FILE    = "trade_log.json"
SENT_LOG       = ".alert_sent_log.json"

# Priority thresholds
PULL_SCORE_MIN  = 65
WATCH_SCORE_MIN = 40
HEAT_MIN        = 1.2
MOVE_MIN        = 3.0


# ----------------------------
# LOADERS
# ----------------------------

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            return default
    return default


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# ----------------------------
# DEDUP — don't spam same signal
# ----------------------------

def load_sent_log():
    return load_json(SENT_LOG, {})


def already_sent(sent_log, symbol, call):
    key = f"{symbol}:{call}"
    return key in sent_log


def mark_sent(sent_log, symbol, call):
    key = f"{symbol}:{call}"
    sent_log[key] = True
    # Keep log from growing forever — prune to last 200
    if len(sent_log) > 200:
        keys = list(sent_log.keys())
        for k in keys[:len(keys) - 200]:
            del sent_log[k]
    return sent_log


# ----------------------------
# PRIORITY LOGIC
# ----------------------------

def get_priority(coin):
    score = float(coin.get("score", 0))
    heat  = float(coin.get("volume_heat", 0))
    move  = float(coin.get("change_24h", coin.get("change", 0)))
    comp  = float(coin.get("compression_bonus", 0))
    tier  = coin.get("quality_tier", "MIDCAP")

    if tier == "HAZARD":
        return None, None

    # PULL — highest priority
    if comp >= 20 and score >= PULL_SCORE_MIN and heat >= HEAT_MIN:
        return "PULL", 1

    # HIGH WATCH — strong move + heat
    if score >= 90 or (heat >= 2.2 and move >= 5):
        return "WATCH", 2

    # STANDARD WATCH
    if score >= WATCH_SCORE_MIN and (heat >= HEAT_MIN or move >= MOVE_MIN):
        return "WATCH", 3

    return None, None


# ----------------------------
# CHIMTU MESSAGE BUILDER
# ----------------------------

def chimtu_message(coin, call, priority, is_discovery=False):
    symbol = coin.get("symbol", "—")
    score  = float(coin.get("score", coin.get("discovery_score", 0)))
    price  = float(coin.get("price", 0))
    move   = float(coin.get("change_24h", coin.get("change", 0)))
    heat   = float(coin.get("volume_heat", 0))
    comp   = float(coin.get("compression_bonus", 0))
    note   = coin.get("setup_note", "")
    tier   = coin.get("quality_tier", "MIDCAP")
    moonshot = coin.get("moonshot_bias", "OFF")

    # Priority emoji + header
    if call == "PULL" and priority == 1:
        header = "🚨 PULL TRIGGER"
    elif call == "WATCH" and priority == 2:
        header = "🔥 HIGH WATCH"
    elif is_discovery:
        header = "🛸 DISCOVERY"
    else:
        header = "👀 WATCH"

    # Chimtu one-line read
    if call == "PULL":
        if comp >= 20:
            read = f"Compression loaded and heat is real — this is the one I'd move on."
        else:
            read = f"Score and heat line up. I'd pull on this one."
    elif call == "WATCH":
        if move >= 10:
            read = f"Already moving hard — don't chase, but keep it on screen."
        elif heat >= 2:
            read = f"Volume is getting loud on this. Watch closely."
        elif comp >= 20:
            read = f"Compression building. Could break either way, stay alert."
        else:
            read = f"Not screaming buy yet, but worth having on the radar."
    else:
        read = f"Something's happening here. Early look."

    if moonshot == "ON":
        read += " Moonshot mode on — size small if you go."

    if note:
        read += f" [{note}]"

    # Format price nicely
    if price < 0.01:
        price_str = f"${price:.6f}"
    elif price < 1:
        price_str = f"${price:.4f}"
    else:
        price_str = f"${price:.2f}"

    move_arrow = "▲" if move >= 0 else "▼"
    disc_tag   = " · 🛸 discovery" if is_discovery else ""

    msg = (
        f"{header}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"*{symbol}*  ·  {tier.lower()}{disc_tag}\n"
        f"\n"
        f"💬 _{read}_\n"
        f"\n"
        f"📊  Score `{score:.0f}`  ·  Heat `{heat:.2f}×`\n"
        f"{move_arrow}  Move `{move:+.2f}%`  ·  Price `{price_str}`\n"
        f"📦  Compression `{comp:.0f}pts`\n"
        f"\n"
        f"— Chimtu"
    )

    return msg


def chimtu_summary_message(ranked, trades):
    wins     = len([t for t in trades if t.get("status") == "WIN"])
    losses   = len([t for t in trades if t.get("status") == "LOSS"])
    total    = wins + losses
    open_cnt = len([t for t in trades if t.get("status") == "OPEN"])
    winrate  = round((wins / total) * 100, 1) if total > 0 else 0.0

    top = ranked[0] if ranked else {}
    symbol = top.get("symbol", "—")
    move   = float(top.get("change_24h", 0))
    heat   = float(top.get("volume_heat", 0))
    score  = float(top.get("score", 0))

    mood = "risk on 🟢" if move > 3 and heat > 1.2 else ("quiet 🟡" if move > -2 else "risk off 🔴")

    if winrate >= 60:
        model_read = f"Model's cooking at {winrate:.1f}% — stay disciplined."
    elif winrate < 45 and total >= 5:
        model_read = f"Win rate dipped to {winrate:.1f}% — tighten entries."
    else:
        model_read = f"Win rate sitting at {winrate:.1f}% over {total} trades."

    msg = (
        f"📡 *Chimtu Pipeline Update*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"Lead: *{symbol}*  ·  score `{score:.0f}`\n"
        f"Move `{move:+.2f}%`  ·  Heat `{heat:.2f}×`\n"
        f"Mood: {mood}\n"
        f"\n"
        f"📈 {model_read}\n"
        f"Open trades: `{open_cnt}`\n"
        f"\n"
        f"— Chimtu"
    )

    return msg


# ----------------------------
# SEND
# ----------------------------

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = urllib.parse.urlencode({
        "chat_id":    CHAT_ID,
        "text":       message,
        "parse_mode": "Markdown"
    }).encode("utf-8")

    try:
        req = urllib.request.Request(url, data=payload, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            if result.get("ok"):
                print(f"[chimtu] ✓ sent → {message[:60].strip()}...")
                return True
            else:
                print(f"[chimtu] ✗ api error: {result}")
                return False
    except urllib.error.HTTPError as e:
        print(f"[chimtu] ✗ http error {e.code}: {e.read().decode()}")
        return False
    except Exception as e:
        print(f"[chimtu] ✗ failed: {e}")
        return False


# ----------------------------
# MAIN ALERT RUNNER
# ----------------------------

def run_alerts(send_summary=True, force=False):
    market      = load_json(MARKET_FILE, [])
    discoveries = load_json(DISCOVERY_FILE, [])
    trades      = load_json(TRADES_FILE, [])
    sent_log    = load_sent_log()

    if not market:
        print("[chimtu] no market data — skipping alerts")
        return

    # Dedup: prefer USD > USDC > USDT per base coin
    quote_rank = {"/USD": 0, "/USDC": 1, "/USDT": 2}
    seen_bases = {}
    for coin in sorted(market, key=lambda x: float(x.get("score", 0)), reverse=True):
        sym = coin.get("symbol", "")
        if "/" not in sym:
            continue
        base, quote = sym.split("/", 1)
        qkey = f"/{quote}"
        if base not in seen_bases:
            seen_bases[base] = coin
        elif quote_rank.get(qkey, 99) < quote_rank.get("/" + seen_bases[base].get("symbol","").split("/")[1], 99):
            seen_bases[base] = coin

    ranked = sorted(seen_bases.values(), key=lambda x: float(x.get("score", 0)), reverse=True)

    alerts_sent = 0

    # ── Market signals ────────────────────────────────────────────────────
    for coin in ranked[:10]:
        call, priority = get_priority(coin)
        if not call:
            continue

        symbol = coin.get("symbol", "")

        if not force and already_sent(sent_log, symbol, call):
            continue

        msg = chimtu_message(coin, call, priority)
        if send_telegram(msg):
            sent_log = mark_sent(sent_log, symbol, call)
            alerts_sent += 1

    # ── Discovery signals ─────────────────────────────────────────────────
    if discoveries:
        disc_sorted = sorted(discoveries, key=lambda x: float(x.get("discovery_score", 0)), reverse=True)
        for coin in disc_sorted[:3]:
            symbol = coin.get("symbol", "")
            disc_score = float(coin.get("discovery_score", 0))

            if disc_score < 100:
                continue

            call = "WATCH"
            priority = 3

            if not force and already_sent(sent_log, f"DISC:{symbol}", call):
                continue

            msg = chimtu_message(coin, call, priority, is_discovery=True)
            if send_telegram(msg):
                sent_log = mark_sent(sent_log, f"DISC:{symbol}", call)
                alerts_sent += 1

    # ── Pipeline summary ──────────────────────────────────────────────────
    if send_summary and ranked:
        msg = chimtu_summary_message(ranked, trades)
        send_telegram(msg)

    save_json(SENT_LOG, sent_log)
    print(f"[chimtu] done — {alerts_sent} alert(s) sent")


# ----------------------------
# ENTRY POINTS
# ----------------------------

if __name__ == "__main__":
    import sys

    # python telegram_alert.py --force   → resend everything ignoring dedup
    # python telegram_alert.py --quiet   → no summary, just signals
    # python telegram_alert.py           → normal run

    force   = "--force" in sys.argv
    quiet   = "--quiet" in sys.argv
    summary = not quiet

    run_alerts(send_summary=summary, force=force)