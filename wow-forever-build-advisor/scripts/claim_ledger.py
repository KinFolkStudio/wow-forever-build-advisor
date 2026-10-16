#!/usr/bin/env python3
"""Fact ledger for the WoW Forever Build Advisor.

Records each fact with its sources and decides, by fixed rules, whether the
fact is VERIFIED, CONFLICT, UNCONFIRMED, or STALE. Uses only the Python
standard library so it runs anywhere.

Tiers: 1 = Blizzard, 2 = trusted guide or data site, 3 = not trusted.
"""
import argparse
import json
import os
import sys
from datetime import date

DEFAULT_PATH = "ledger.json"


def parse_day(text, label):
    try:
        return date.fromisoformat(text)
    except (TypeError, ValueError):
        sys.exit(f"Error: {label} must be a date like 2026-10-16, got {text!r}")


def norm(value):
    return "".join(str(value).lower().split())


def load(path):
    if not os.path.exists(path):
        sys.exit(f"Error: no ledger at {path}. Run 'init' first.")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save(path, data):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def is_current(src, cutoff, today, changed=None):
    if src["date"] == "undated":
        return False
    d = date.fromisoformat(src["date"])
    if d > today:
        return False
    if src["tier"] == 1:
        # Blizzard's own word stands until Blizzard changes that topic,
        # even if it is older than the starting point.
        return changed is None or d >= changed
    return d >= cutoff


def undated_blizzard(sources):
    return [s for s in sources if s["date"] == "undated" and s["tier"] == 1]


def claim_cutoff(claim, floor):
    changed = claim.get("changed")
    if changed and date.fromisoformat(changed["date"]) > floor:
        return date.fromisoformat(changed["date"])
    return floor


def judge(claim, floor, today):
    """Return (status, value, note) for one claim."""
    cutoff = claim_cutoff(claim, floor)
    changed = date.fromisoformat(claim["changed"]["date"]) if claim.get("changed") else None
    sources = claim["sources"]
    current = [s for s in sources if is_current(s, cutoff, today, changed)]
    # An undated Blizzard page cannot verify a fact alone, but it counts as one
    # trusted publisher ("Blizzard") toward the two-site rule.
    current += [dict(s, tier=2, publisher="Blizzard (undated)") for s in undated_blizzard(sources)
                if any(o["tier"] in (1, 2) and is_current(o, cutoff, today, changed) for o in sources)]
    trusted_current = [s for s in current if s["tier"] in (1, 2)]

    if not trusted_current:
        if any(s["tier"] in (1, 2) and s["date"] != "undated" for s in sources):
            return "STALE", None, f"Every trusted source is older than the last update that changed this ({cutoff})."
        if undated_blizzard(sources):
            return "UNCONFIRMED", None, "Only an undated Blizzard page; need one current trusted site that agrees."
        return "UNCONFIRMED", None, "No trusted source yet."

    tier1 = [s for s in trusted_current if s["tier"] == 1]
    tier2 = [s for s in trusted_current if s["tier"] == 2]

    if tier1:
        values = {norm(s["value"]) for s in tier1}
        if len(values) > 1:
            return "CONFLICT", None, "Blizzard sources give different values; use the newest Blizzard post and say so."
        value = tier1[0]["value"]
        dissent = sorted({s["publisher"] for s in tier2 if norm(s["value"]) != norm(value)})
        note = "Confirmed by Blizzard."
        if dissent:
            note += " These sites say otherwise: " + ", ".join(dissent) + "."
        return "VERIFIED", value, note

    by_value = {}
    for s in tier2:
        by_value.setdefault(norm(s["value"]), {"value": s["value"], "publishers": set()})
        by_value[norm(s["value"])]["publishers"].add(norm(s["publisher"]))

    if len(by_value) > 1:
        parts = [f"{v['value']} ({len(v['publishers'])} site(s))" for v in by_value.values()]
        return "CONFLICT", None, "Trusted sites disagree: " + "; ".join(parts) + "."

    only = next(iter(by_value.values()))
    if len(only["publishers"]) >= 2:
        return "VERIFIED", only["value"], f"{len(only['publishers'])} different trusted sites agree."
    return "UNCONFIRMED", only["value"], "Only one trusted site so far; need a second, different site."


def cmd_init(args):
    today = parse_day(args.today, "--today")
    cutoff = parse_day(args.cutoff, "--cutoff")
    if cutoff > today:
        sys.exit("Error: the latest update date cannot be after today.")
    save(args.ledger, {"today": str(today), "cutoff": str(cutoff), "version": args.version, "claims": {}})
    print(f"Ledger started. Today {today}. Starting point {cutoff} ({args.version}).")


def cmd_add(args):
    data = load(args.ledger)
    today = date.fromisoformat(data["today"])
    if args.date.lower() == "undated":
        if args.tier != 1:
            sys.exit("Error: only Blizzard pages may be recorded without a date. Find a dated page instead.")
        d = "undated"
    else:
        d = parse_day(args.date, "--date")
        if d > today:
            sys.exit("Error: a source cannot be dated after today. Check the date on the page.")
    if args.tier not in (1, 2, 3):
        sys.exit("Error: --tier must be 1, 2, or 3.")
    claim = data["claims"].setdefault(args.id, {"topic": args.topic, "sources": []})
    if args.topic:
        claim["topic"] = args.topic
    for s in claim["sources"]:
        if s["url"] == args.url:
            sys.exit("Error: that page is already recorded for this fact.")
    claim["sources"].append({
        "value": args.value, "url": args.url, "publisher": args.publisher,
        "tier": args.tier, "date": str(d),
    })
    save(args.ledger, data)
    status, value, note = judge(claim, date.fromisoformat(data["cutoff"]), today)
    print(f"Added. {args.id}: {status}. {note}")


def cmd_changed(args):
    data = load(args.ledger)
    today = date.fromisoformat(data["today"])
    d = parse_day(args.date, "--date")
    if d > today:
        sys.exit("Error: an update cannot be dated after today.")
    claim = data["claims"].setdefault(args.id, {"topic": args.topic, "sources": []})
    if args.topic:
        claim["topic"] = args.topic
    old = claim.get("changed")
    if old is None or d >= date.fromisoformat(old["date"]):
        claim["changed"] = {"date": str(d), "url": args.url, "note": args.note}
    save(args.ledger, data)
    status, value, note = judge(claim, date.fromisoformat(data["cutoff"]), today)
    print(f"Recorded. {args.id} was last changed by Blizzard on {claim['changed']['date']}. Now: {status}. {note}")


def cmd_report(args):
    data = load(args.ledger)
    cutoff = date.fromisoformat(data["cutoff"])
    today = date.fromisoformat(data["today"])
    rows = []
    for cid, claim in sorted(data["claims"].items()):
        status, value, note = judge(claim, cutoff, today)
        rows.append({"id": cid, "topic": claim.get("topic"), "status": status,
                     "too_old_if_before": str(claim_cutoff(claim, cutoff)),
                     "value": value, "note": note,
                     "sources": [f"{s['publisher']} ({s['date']}) {s['url']}" for s in claim["sources"]]})
    if args.json:
        print(json.dumps({"today": data["today"], "cutoff": data["cutoff"],
                          "version": data["version"], "claims": rows}, indent=2))
        return
    print(f"Checked on {data['today']} against WoW Forever {data['version']}. Starting point: {data['cutoff']}.")
    counts = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
        shown = f" = {r['value']}" if r["value"] is not None and r["status"] == "VERIFIED" else ""
        print(f"[{r['status']}] {r['id']} ({r['topic']}){shown}. {r['note']}")
    print("Totals: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ledger", default=DEFAULT_PATH)
    sub = p.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("init")
    i.add_argument("--today", required=True)
    i.add_argument("--cutoff", required=True, help="starting point: launch day, or the latest update that changed the whole game")
    i.add_argument("--version", required=True, help="patch or build name")
    i.set_defaults(func=cmd_init)

    a = sub.add_parser("add")
    a.add_argument("--id", required=True)
    a.add_argument("--topic", default="")
    a.add_argument("--value", required=True)
    a.add_argument("--url", required=True)
    a.add_argument("--publisher", required=True)
    a.add_argument("--tier", type=int, required=True)
    a.add_argument("--date", required=True, help="YYYY-MM-DD, or 'undated' for a Blizzard page with no date")
    a.set_defaults(func=cmd_add)

    c = sub.add_parser("changed", help="record the latest Blizzard update that changed this fact's topic")
    c.add_argument("--id", required=True)
    c.add_argument("--topic", default="")
    c.add_argument("--date", required=True)
    c.add_argument("--url", required=True)
    c.add_argument("--note", required=True, help="what the update changed, in a few words")
    c.set_defaults(func=cmd_changed)

    r = sub.add_parser("report")
    r.add_argument("--json", action="store_true")
    r.set_defaults(func=cmd_report)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
