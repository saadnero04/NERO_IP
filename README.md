# Automatically NERO IP using Tor
A Python script to automatically change your IP address using the Tor network. This script can change your IP at regular intervals, with the option for infinite mode, and will display the new IP in the terminal.

Features

Change IP automatically using Tor.
Option to set a time interval between IP changes.
Option to change IP a specific number of times or infinitely.
Color-coded output for new IP address (Green).

Requirements

Before using the script, make sure you have the following dependencies installed:

Python 3
Tor running on your machine

---

# Problem Channel: faceless AI-character Shorts

Finds problems people are asking about right now (Reddit and YouTube search),
then uses Claude to write a full Short. Two recurring AI characters explain the
problem and the fix. You get the hook, script, visual prompts for each scene,
title, hashtags and a thumbnail prompt.

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...          # from console.anthropic.com
python -m problem_channel find        # see the trending problems
python -m problem_channel make --count 5
python -m problem_channel make --problem "How to stop overthinking at night"
```

Output goes to `videos/<date>/`. Paste the scene prompts into your AI video tool
and voice the lines with TTS. See `examples/wake-up-tired.md`.
