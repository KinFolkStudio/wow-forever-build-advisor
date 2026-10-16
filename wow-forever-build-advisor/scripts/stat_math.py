#!/usr/bin/env python3
"""Stat and gear math for the WoW Forever Build Advisor.

Every input must come from a VERIFIED fact in the ledger. This script does
not contain any game numbers of its own, so it cannot go out of date.
Uses only the Python standard library.
"""
import argparse
import sys


def positive(x, label):
    if x < 0:
        sys.exit(f"Error: {label} cannot be negative.")
    return x


def rating_to_percent(rating, per_percent):
    if per_percent <= 0:
        sys.exit("Error: rating per 1% must be more than zero.")
    return rating / per_percent


def rating_needed(target, have, per_percent):
    missing = max(0.0, target - have)
    return missing, missing * per_percent


def crit_cap(miss, dodge, parry, block, glancing, suppression):
    """Highest crit chance that can still land on auto attacks.

    The attack table has 100 slots. Misses, dodges, parries, blocks, and
    glancing blows are rolled first; crit only gets what is left.
    """
    used = miss + dodge + parry + block + glancing + suppression
    return max(0.0, 100.0 - used), used


def parse_pairs(text, label):
    out = {}
    if not text:
        return out
    for part in text.split(","):
        if "=" not in part:
            sys.exit(f"Error: {label} must look like name=number,name=number")
        k, v = part.split("=", 1)
        try:
            out[k.strip().lower()] = float(v)
        except ValueError:
            sys.exit(f"Error: {v!r} in {label} is not a number.")
    return out


def score(item, weights):
    unknown = [k for k in item if k not in weights]
    if unknown:
        sys.exit("Error: no verified weight for: " + ", ".join(unknown) +
                 ". Compare these in words instead.")
    return sum(v * weights[k] for k, v in item.items())


def fmt(x):
    return f"{x:.2f}".rstrip("0").rstrip(".")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("rating-to-percent")
    a.add_argument("--rating", type=float, required=True)
    a.add_argument("--per-percent", type=float, required=True)

    b = sub.add_parser("rating-needed")
    b.add_argument("--target", type=float, required=True, help="percent you want")
    b.add_argument("--have", type=float, default=0.0, help="percent you already get from talents and gear")
    b.add_argument("--per-percent", type=float, required=True)

    c = sub.add_parser("crit-cap")
    for name in ("miss", "dodge", "parry", "block", "glancing", "suppression"):
        c.add_argument(f"--{name}", type=float, default=0.0)
    c.add_argument("--crit", type=float, help="your crit chance, to see how much is wasted")

    d = sub.add_parser("compare-items")
    d.add_argument("--weights", required=True)
    d.add_argument("--a", required=True)
    d.add_argument("--b", required=True)

    args = p.parse_args()

    if args.cmd == "rating-to-percent":
        pct = rating_to_percent(positive(args.rating, "rating"), args.per_percent)
        print(f"{fmt(args.rating)} rating = {fmt(pct)}%")
    elif args.cmd == "rating-needed":
        missing, rating = rating_needed(args.target, positive(args.have, "have"), args.per_percent)
        if missing == 0:
            print(f"Already at or above {fmt(args.target)}%. No more needed.")
        else:
            print(f"Need {fmt(missing)}% more, which is {fmt(rating)} rating.")
    elif args.cmd == "crit-cap":
        vals = [positive(getattr(args, n), n) for n in ("miss", "dodge", "parry", "block", "glancing", "suppression")]
        cap, used = crit_cap(*vals)
        print(f"Other results use {fmt(used)}% of attacks. Crit cap on auto attacks: {fmt(cap)}%.")
        if args.crit is not None:
            wasted = max(0.0, args.crit - cap)
            print(f"Your crit {fmt(args.crit)}%: " + (f"{fmt(wasted)}% is wasted." if wasted else "nothing wasted."))
    elif args.cmd == "compare-items":
        w = parse_pairs(args.weights, "--weights")
        sa, sb = score(parse_pairs(args.a, "--a"), w), score(parse_pairs(args.b, "--b"), w)
        print(f"Item A score {fmt(sa)}, Item B score {fmt(sb)}.")
        if abs(sa - sb) < 1e-9:
            print("They are equal by these weights.")
        else:
            better, diff = ("A", sa - sb) if sa > sb else ("B", sb - sa)
            pct = diff / max(min(sa, sb), 1e-9) * 100
            print(f"Item {better} is ahead by {fmt(diff)} points ({fmt(pct)}%).")


if __name__ == "__main__":
    main()
