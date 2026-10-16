# WoW Forever Build Advisor

A free skill for Claude (an AI assistant you chat with). A skill is a set of instructions that teaches Claude a new job. This one gives you checked, up-to-date advice for World of Warcraft Forever: talents, stats, gear, professions, dual spec, and getting ready for raids, for every class and spec.

You ask it questions in plain words, like you would ask a guildmate. It looks things up on the internet that same day, checks them against Blizzard and trusted guide sites, and tells you what is confirmed, what trusted sites disagree on, and what is not confirmed yet. It never makes things up.

You do not need to know anything about AI to use it. The steps below walk you through everything, one click at a time.

## What you need

- A computer with a web browser (Chrome, Edge, Safari, or Firefox). You can chat from your phone later, but the setup is easiest on a computer.
- A free Claude account. As of October 2026, the free plan works with this skill. Paid plans give you more messages per day.
- If your Claude account comes from work or school (a Team or Enterprise plan), an admin may have turned off uploading skills or web search. If you cannot find those settings, ask your admin to turn them on.
- The file named `wow-forever-build-advisor.zip` from this page.

## Setup (about 10 minutes, one time only)

### Step 1: Make a free Claude account

1. Go to **claude.ai** in your web browser.
2. Sign up with your email or your Google account.
3. Pick the **Free** plan if it asks.

### Step 2: Turn on the setting the skill needs

The skill uses a small built-in calculator to do the math, so one setting must be on.

1. In Claude, click your name or picture in the bottom left corner.
2. Click **Settings**.
3. Click **Capabilities**.
4. Find **Code execution and file creation** and turn it **on**.

### Step 3: Download the skill file

1. Click this link: **[Download wow-forever-build-advisor.zip](https://github.com/KinFolkStudio/wow-forever-build-advisor/raw/main/wow-forever-build-advisor.zip)**
2. The file goes to your **Downloads** folder.

If the link does not work, click the file named **wow-forever-build-advisor.zip** in the list of files at the top of this page, then click the **download** button (a small arrow pointing down, on the right side).

**Do not open or unzip the file.** Claude needs it zipped exactly as it is.

If you use a Mac with Safari, Safari may unzip it on its own and leave a folder instead of a `.zip` file. If that happens, either download it again using Chrome, or right-click the folder, choose **Compress**, and use the new `.zip` file it makes.

### Step 4: Add it to Claude

1. In Claude, open **Customize**, then **Skills**.
2. Click the **+** button, then **+ Create skill**.
3. Click **Upload a skill**.
4. Pick the **wow-forever-build-advisor.zip** file from your Downloads folder.
5. It now shows in your list of skills. Make sure the switch next to it is **on**.

Claude's menus sometimes move around. If something looks different, look for the word **Skills** in the menu on the left side of Claude.

### Step 5: Make sure Claude can search the web

The skill needs to look things up online.

1. Start a new chat.
2. Click the **+** button at the bottom left of the message box.
3. If you see **Web search**, click it so a checkmark shows next to it.

If you do not see a **Web search** option at all, that is fine: your Claude already searches the web on its own when it needs to.

That's it. You're set up.

## How to use it

Start a new chat and just ask. Mentioning "WoW Forever" helps Claude know to use the skill. Some examples:

- "I play a Human Warrior in WoW Forever. Help me pick a build for raids."
- "What is the stat priority for a Holy Priest in WoW Forever?"
- "How much hit do I need as a Rogue in WoW Forever?"
- "Which professions are best for a Mage in WoW Forever?"
- "I have dual spec on my Druid. What should my two specs be if I tank in raids and do PvP on the side?"
- "Make me a table comparing the talent choices for Retribution Paladin."
- "Make me a document with my full Hunter plan that I can keep."

The first time, it may ask you a few quick questions (your class, spec, level, professions, and how you like to play) so its advice fits you. If you just want a quick answer, say "no questions, just tell me."

Good answers take a little time because it is checking several websites. Give it a minute or two.

## How to read its answers

- **Confirmed:** Blizzard says it, or at least two trusted guide sites agree, and they are newer than the last game change to that topic.
- **Trusted sources disagree:** It shows you both choices, who suggests each one, the pros and cons, and suggests you test both (for example, on a training dummy).
- **Not confirmed yet:** It could not check this well enough today. Ask again in a few days, especially right after a patch.
- Every answer ends with a **Checked on** date and links to its sources, so you can see exactly where the information came from.

When there are several good choices, it will not pick one for you. It shows what each choice is good at and what kind of player it fits, then lets you decide.

## Where the information comes from

- **Blizzard:** official news, patch notes, hotfixes, class deep dives, and staff posts on the official forums.
- **Trusted guide sites:** Icy Veins, Wowhead, Method, Warcraft Tavern, wow.gg, and Warcraft Logs (real player results).

It does not use Reddit, player forum posts, YouTube creators, or guides for other versions of the game as proof. It cannot watch videos, so anything said only in a video counts as not confirmed until Blizzard or a trusted site writes it down.

## If something goes wrong

| What you see | What to do |
| --- | --- |
| The upload fails | Make sure you picked the `.zip` file, not a folder, and that you did not rename it. Download it again if needed. |
| It doesn't seem to use the skill | Check that its switch is on in **Customize, Skills**. Then include "WoW Forever" in your question, or say "Use the WoW Forever Build Advisor skill." |
| It says it can't run code or calculate | Turn on **Code execution and file creation** in **Settings, Capabilities** (Step 2). |
| It can't look anything up | Turn on **Web search** (Step 5). |
| Lots of "not confirmed yet" | Normal right after a patch or during testing. Guide sites usually catch up within a few days. Ask again later. |
| You hit a message limit | The free plan has a limit that resets every five hours. Each web search counts toward it, and a full build answer checks many websites, so free players can reach the limit sooner than in a normal chat. Wait and try again, ask about one topic at a time (for example, only talents), or consider a paid plan if you use it a lot. |

## Privacy

It only needs game information: class, spec, level, professions, and how you like to play. Never share your Battle.net login, password, or personal details with it or anyone.

## How to keep this up to date

The skill does not need updates to stay current, because it looks everything up fresh each time you ask. It only changes when its instructions change (for example, when a trusted website is added).

What's inside:

| File | What it does |
| --- | --- |
| `wow-forever-build-advisor/SKILL.md` | The main instructions Claude follows |
| `wow-forever-build-advisor/references/onboarding.md` | The quick player interview |
| `wow-forever-build-advisor/references/sources.md` | Which websites are trusted |
| `wow-forever-build-advisor/references/verification.md` | The fact-checking rules |
| `wow-forever-build-advisor/references/output-style.md` | How answers are written so anyone aged 8 to 80 can follow them |
| `wow-forever-build-advisor/scripts/claim_ledger.py` | Keeps track of each fact and decides if it is confirmed |
| `wow-forever-build-advisor/scripts/stat_math.py` | Does all the math |
| `wow-forever-build-advisor.zip` | The ready-to-upload skill file |
| `tests/` | Automatic checks for the two Python tools (not part of the skill) |

**To get a newer version:** download the `.zip` file again (Step 3), then in Claude delete the old skill and upload the new one (Step 4).

**If you change the skill yourself:** after editing anything in the `wow-forever-build-advisor` folder, rebuild the `.zip` file. Right-click the folder itself (not the files inside it). On Windows, choose **Compress to**, then **ZIP file**. On a Mac, choose **Compress**. Name the new file exactly `wow-forever-build-advisor.zip`. To run the automatic checks, open a terminal in this folder and run `python -m unittest discover tests`.

**Using a different AI assistant:** you can read these files and adapt them. The fact-checking and math tools are plain Python with nothing extra to install.

## License

MIT. See [LICENSE](LICENSE).
