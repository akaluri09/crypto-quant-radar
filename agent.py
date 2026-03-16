import json
import os

MARKET_FILE    = "market_radar.json"
DISCOVERY_FILE = "discovery_radar.json"
TRADES_FILE    = "trade_log.json"


# ----------------------------
# LOADERS
# ----------------------------

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            return default
    return default


# ----------------------------
# CLASSIFICATION
# ----------------------------

MEME = {
    "PEPE", "DOGE", "SHIB", "FLOKI", "BONK", "TRUMP",
    "FARTCOIN", "USELESS", "WIF", "MOG", "POPCAT", "TURBO", "PENGU"
}

HAZARD = {"UP", "DOWN", "XAN", "A8", "OPN"}

LEGIT = {
    "BTC", "ETH", "SOL", "ADA", "LINK", "AVAX", "MATIC", "ATOM",
    "FET", "TAO", "ALGO", "XRP", "BCH", "LTC", "DOT", "ARB", "OP",
    "HBAR", "ICP", "AAVE", "CRV", "RENDER", "FIL", "NEAR", "INJ",
    "UNI", "DOGE"
}


def classify_risk(symbol):
    base = symbol.split("/")[0]
    if base in HAZARD:
        return "hazard"
    if base in MEME:
        return "meme"
    if base in LEGIT:
        return "legit"
    return "spec"


# ----------------------------
# DEDUP: prefer USD > USDC > USDT
# ----------------------------

def prefer_primary_quotes(coins):
    rank = {"/USD": 0, "/USDC": 1, "/USDT": 2}
    chosen = {}

    for coin in coins:
        symbol = coin.get("symbol", "")
        if "/" not in symbol:
            continue
        base, quote = symbol.split("/", 1)
        quote_key = f"/{quote}"

        if base not in chosen:
            chosen[base] = coin
            continue

        existing = chosen[base].get("symbol", "")
        existing_quote = "/" + existing.split("/")[1] if "/" in existing else "/ZZZ"
        if rank.get(quote_key, 99) < rank.get(existing_quote, 99):
            chosen[base] = coin

    return list(chosen.values())


# ----------------------------
# ACTION LOGIC
# ----------------------------

def action_call(coin):
    score = float(coin.get("score", 0))
    heat  = float(coin.get("volume_heat", 0))
    move  = float(coin.get("change_24h", coin.get("change", 0)))
    comp  = float(coin.get("compression_bonus", 0))
    tier  = coin.get("quality_tier", "MIDCAP")
    risk  = classify_risk(coin.get("symbol", ""))

    if tier == "HAZARD" or risk == "hazard":
        return "AVOID"

    if risk == "meme" and comp == 0 and move < 5:
        return "AVOID"

    if comp >= 20 and score >= 65 and risk in ("legit", "spec"):
        return "PULL"

    if score >= 90 or heat >= 2.2 or move >= 8:
        return "WATCH"

    return "WATCH"


# ----------------------------
# MARKET MOOD
# ----------------------------

def market_mood(move, heat):
    if move >= 5 and heat >= 1.5:
        return "Risk On — momentum and volume aligned"
    if move >= 2:
        return "Mild Bullish — directional but not explosive"
    if move <= -5:
        return "Risk Off — weakness in lead name"
    return "Neutral — no dominant direction yet"


# ----------------------------
# MAIN
# ----------------------------

def main():
    market     = load_json(MARKET_FILE, [])
    discoveries = load_json(DISCOVERY_FILE, [])
    trades     = load_json(TRADES_FILE, [])

    # ── No data guard ──────────────────────────────────────────────────────
    if not market:
        print("SUMMARY: No market radar data available yet.")
        print("MARKET_READ: Run scanner.py first to generate ranked market context.")
        print("RISK: No assistant guidance can be produced without radar data.")
        return

    # ── Prep ranked list ───────────────────────────────────────────────────
    ranked = sorted(market, key=lambda x: float(x.get("score", 0)), reverse=True)
    ranked = prefer_primary_quotes(ranked)

    top = ranked[0]

    top_symbol   = top.get("symbol", "—")
    top_score    = float(top.get("score", 0))
    top_price    = float(top.get("price", 0))
    top_move     = float(top.get("change_24h", top.get("change", 0)))
    top_heat     = float(top.get("volume_heat", 0))
    top_short    = float(top.get("short_momentum", 0))
    top_comp     = float(top.get("compression_bonus", 0))
    top_tier     = top.get("quality_tier", "MIDCAP")
    top_note     = top.get("setup_note", "No setup note.")
    top_moonshot = top.get("moonshot_bias", "OFF")
    top_call     = action_call(top)
    top_risk     = classify_risk(top_symbol)

    # ── Trade stats ────────────────────────────────────────────────────────
    wins      = len([t for t in trades if t.get("status") == "WIN"])
    losses    = len([t for t in trades if t.get("status") == "LOSS"])
    open_cnt  = len([t for t in trades if t.get("status") == "OPEN"])
    total     = wins + losses
    winrate   = round((wins / total) * 100, 1) if total > 0 else 0.0

    # ── Classify supporting names ──────────────────────────────────────────
    clean_picks = []
    weak_names  = []
    meme_names  = []

    for coin in ranked[:12]:
        sym  = coin.get("symbol", "")
        risk = classify_risk(sym)
        comp = float(coin.get("compression_bonus", 0))
        sc   = float(coin.get("score", 0))

        if risk in ("hazard", "meme"):
            if risk == "meme":
                meme_names.append(sym)
            else:
                weak_names.append(sym)
        elif comp >= 20 and sc >= 60:
            clean_picks.append(sym)

    clean_picks = clean_picks[:4]
    weak_names  = weak_names[:3]
    meme_names  = meme_names[:3]

    # ── Top discovery ──────────────────────────────────────────────────────
    top_disc = None
    if discoveries:
        disc_sorted = sorted(
            discoveries,
            key=lambda x: float(x.get("discovery_score", 0)),
            reverse=True
        )
        disc_sorted = prefer_primary_quotes(disc_sorted)
        if disc_sorted:
            top_disc = disc_sorted[0]

    # ── Build output strings — Chimtu voice ───────────────────────────────
    mood = market_mood(top_move, top_heat)

    # SUMMARY — punchy opener
    if top_move >= 15:
        move_flavor = f"up {top_move:.1f}% — yeah, it's moving"
    elif top_move >= 5:
        move_flavor = f"nudging {top_move:.1f}% on the day, respectable"
    elif top_move > 0:
        move_flavor = f"creeping {top_move:.1f}% — slow but it's something"
    elif top_move > -5:
        move_flavor = f"down {abs(top_move):.1f}%, nothing alarming yet"
    else:
        move_flavor = f"bleeding {abs(top_move):.1f}% — worth watching"

    if top_comp >= 20:
        comp_flavor = f"solid {top_comp:.0f}-point compression behind it"
    else:
        comp_flavor = "no compression to speak of — momentum-only setup"

    summary = (
        f"Hey, {top_symbol} is my top read right now. "
        f"Score sitting at {top_score:.0f}, {move_flavor}, "
        f"heat at {top_heat:.2f}×, and {comp_flavor}. "
        f"It's a {top_tier.lower()} name with moonshot {"on" if top_moonshot == "ON" else "off"}."
    )

    # REASON — explain the call with personality
    if top_call == "PULL":
        call_flavor = "I like it enough to say pull the trigger — compression + heat line up"
    elif top_call == "WATCH":
        call_flavor = "not screaming buy, but I'd keep it on the screen"
    else:
        call_flavor = "honestly I'd leave this one alone for now"

    reason = f"{call_flavor}. {top_note}"

    # MARKET READ — opinionated, not robotic
    if top_moonshot == "ON":
        market_read = (
            f"Moonshot mode is live on {top_symbol}. "
            f"These can go parabolic fast, but they can also dump just as quick — don't get greedy. "
            f"Mood out there feels like {mood.lower()}."
        )
    else:
        market_read = (
            f"{top_symbol} is more of a structure play than a moonshot — I actually prefer that. "
            f"Cleaner risk. Market mood is {mood.lower()}."
        )

    if clean_picks:
        if len(clean_picks) == 1:
            market_read += f" Only one name with real compression right now: {clean_picks[0]}. Worth knowing."
        else:
            market_read += f" A few names with actual compression worth watching: {', '.join(clean_picks)}."

    if top_disc:
        disc_sym   = top_disc.get("symbol", "")
        disc_score = float(top_disc.get("discovery_score", 0))
        disc_heat  = float(top_disc.get("volume_heat", 0))
        market_read += (
            f" Oh — and {disc_sym} just showed up on discovery "
            f"(score {disc_score:.0f}, heat {disc_heat:.2f}×). Keep an eye on it."
        )

    # RISK — honest, not a disclaimer
    if total == 0:
        risk_intro = "No closed trades yet so the model's still finding its feet."
    elif winrate < 45:
        risk_intro = f"Win rate is {winrate:.1f}% over {total} trades — below where I want it. Time to tighten up entries."
    elif winrate >= 60:
        risk_intro = f"Win rate at {winrate:.1f}% over {total} trades — model's cooking. Stay disciplined though."
    else:
        risk_intro = f"Win rate is {winrate:.1f}% over {total} trades ({open_cnt} still open) — decent, room to improve."

    risk_parts = [risk_intro]
    risk_parts.append("Don't chase names with no compression just because they're moving — heat alone isn't enough.")

    if weak_names:
        risk_parts.append(f"I'd skip {', '.join(weak_names)} — hazard territory.")
    if meme_names:
        risk_parts.append(f"Meme coins in the mix: {', '.join(meme_names)}. Only if volume is absolutely exceptional, and even then.")

    risk_line = " ".join(risk_parts)

    # ── Print structured output (matches app.py parser keys exactly) ───────
    print(f"SUMMARY: {summary}")
    print(f"TOP_PICK: {top_symbol}")
    print(f"REASON: {reason}")
    print(f"MARKET_READ: {market_read}")
    print(f"RISK: {risk_line}")

    # Lead signal
    print(
        f"SIGNAL: {top_symbol} | {top_call} | "
        f"score {top_score:.1f} • heat {top_heat:.2f}× • move {top_move:+.2f}% • {top_note}"
    )

    # Supporting signals (top 4 after lead)
    for coin in ranked[1:5]:
        sym  = coin.get("symbol", "")
        call = action_call(coin)
        note = coin.get("setup_note", "")
        sc   = float(coin.get("score", 0))
        ht   = float(coin.get("volume_heat", 0))
        mv   = float(coin.get("change_24h", coin.get("change", 0)))
        print(
            f"SIGNAL: {sym} | {call} | "
            f"score {sc:.1f} • heat {ht:.2f}× • move {mv:+.2f}% • {note}"
        )

    # Discovery signal if available
    if top_disc:
        disc_sym  = top_disc.get("symbol", "")
        disc_call = action_call(top_disc)
        disc_note = top_disc.get("setup_note", "Fresh discovery.")
        disc_sc   = float(top_disc.get("discovery_score", 0))
        disc_ht   = float(top_disc.get("volume_heat", 0))
        disc_mv   = float(top_disc.get("change_24h", top_disc.get("change", 0)))
        print(
            f"SIGNAL: {disc_sym} | {disc_call} | "
            f"discovery {disc_sc:.0f} • heat {disc_ht:.2f}× • move {disc_mv:+.2f}% • {disc_note}"
        )


if __name__ == "__main__":
    main()