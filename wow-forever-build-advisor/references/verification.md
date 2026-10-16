# Verification loop

You manage this loop yourself. It has three parts: freshness, the fact ledger, and the second check.

## 1. Freshness

- Get today's date from a clock tool or the conversation. Never assume it.
- Blizzard's own statements (tier 1) are not limited by the starting point: they stand until a later Blizzard update changes that topic. The starting point only limits guide sites.
- Some Blizzard pages hold several updates in one thread (for example, development notes "Updated October 15" with earlier dated posts). Treat each dated post as its own update.
- Set the starting point. Before launch, use the date the current beta began. After launch, use the launch date, or the date of the most recent big patch that Blizzard says changes classes or items across the whole game, whichever is newer. No guide site older than the starting point is ever used.
- Read every Blizzard update since the starting point (patch notes, hotfix notes, development notes). For each fact you are checking, note whether any update changed its topic: the class, spec, talent, ability, stat rule, item, or profession it is about. Record the newest such update with the `changed` command. That date becomes the fact's own cutoff.
- When an update is vague about what it changed (for example "class tuning" with no details), treat it as changing every topic it might touch. Be strict, not hopeful.
- A guide site counts for a fact only if it is dated on or after that fact's cutoff and not after today. Older sources are STALE for that fact.
- If you cannot find Blizzard's updates at all, tell the player, and use the newest Blizzard update you can confirm as the starting point, saying which one.
- Which date to use for the update: the date Blizzard writes in the title or body ("Updated October 15"). If Blizzard writes no date, use the posting date shown on the page. Ignore time zone differences in raw timestamps.
- A Blizzard page with no date at all may be recorded with `--date undated`. It cannot verify a fact by itself, but it counts as one trusted publisher, so it plus one current trusted site that agrees makes the fact VERIFIED. Guide sites with no date cannot be recorded; find a dated page.
- A guide or database page showing the game's own spell, talent, or item text, and saying which game version it is from, is recorded as tier 1 with a publisher like "Wowhead (game text)".

## 2. The fact ledger

Run `scripts/claim_ledger.py`. It keeps facts in a small file (default `ledger.json` in the working folder).

Start a session:

```
python scripts/claim_ledger.py init --today 2026-10-16 --cutoff 2026-09-24 --version "beta, update of October 15"
```

Record a Blizzard update that changed a fact's topic (do this before or after adding sources, either works):

```
python scripts/claim_ledger.py changed --id ret-stat-priority --date 2026-10-15 \
  --url https://... --note "Champion of the Light changed"
```

Add a fact. The value is what the source says, written short and exact, using the same wording for the same answer so the script can tell when sources agree. Add one source per command:

```
python scripts/claim_ledger.py add --id hit-boss-melee --topic "Hit needed vs raid boss" \
  --value "8%" --url https://www.method.gg/... --publisher "Method" --tier 2 --date 2026-10-06
```

Check everything:

```
python scripts/claim_ledger.py report
```

What the statuses mean:

| Status | Rule | How you say it |
| --- | --- | --- |
| VERIFIED | One current Blizzard source, or two current trusted sites from different publishers, all with the same value, and no current trusted source saying something different | State it as fact |
| CONFLICT | Current trusted sources give different values | "Trusted sources disagree", show each with who says it, suggest testing |
| UNCONFIRMED | Only one current trusted site, or only untrusted sources | "Not confirmed yet" |
| STALE | Every source is older than the last Blizzard update that changed this topic | Do not use. Look for newer sources |

A current Blizzard source overrides a Tier 2 site on rules facts (what something does). If Blizzard and a guide site disagree on a rules fact, the script marks it VERIFIED to Blizzard's value but lists the disagreement; mention it if it matters.

For "best" choices (which talent or item is strongest), Blizzard is not the judge; Tier 2 agreement decides.

## 3. The second check

Before you answer:

1. Run `report` and make sure every number and fact you plan to say is VERIFIED, or is labeled as CONFLICT or UNCONFIRMED in your answer.
2. Reopen the sources behind each number and confirm the page says exactly that value, for WoW Forever, with that date. If your tools allow starting a separate checker that did not do the research, give it the ledger and the draft answer and have it do this step; otherwise do it yourself as a fresh pass.
3. Re-run any calculation through `scripts/stat_math.py` and compare to the draft.
4. Remove or relabel anything that fails. Never keep a fact because it "seems right".

## 4. Math

All math uses `scripts/stat_math.py` with inputs that are VERIFIED. Example commands:

```
python scripts/stat_math.py rating-to-percent --rating 70 --per-percent 10
python scripts/stat_math.py rating-needed --target 8 --have 3 --per-percent 10
python scripts/stat_math.py crit-cap --miss 0 --dodge 6.5 --glancing 24
python scripts/stat_math.py compare-items --weights "strength=2.2,crit_rating=1.1" --a "strength=20,crit_rating=14" --b "strength=32"
```

If a talent or item gives hit or crit as a percent instead of a rating, add it to `--have` in rating-needed.

Stat weights used in compare-items must come from VERIFIED sources. If no verified weights exist, compare items in words using the verified stat priority and say an exact score is not possible.
