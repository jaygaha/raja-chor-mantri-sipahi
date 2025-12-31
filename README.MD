# Raja Chor Mantri Sipahi

A simple Python implementation of the traditional role-playing game "Raja Chor Mantri Sipahi" (King, Minister, Thief, Police). We used to play this game when I was a child. I remember it was a lot of fun.

This project is designed for learning Game Development in Python, keeping the code beginner-friendly without complex frameworks.

## Roles & Points
- **Raja** (King): 1000 Points
- **Mantri** (Minister): 800 Points
- **Sipahi** (Police): 500 Points
- **Chor** (Thief): 0 Points

## Phase 2: Smarter Bot AI

In this phase, we added "Personalities" to the Bots to make them feel more human and intelligent. Instead of just guessing randomly, they now use strategies!

### The Strategies
When a Bot joins the game, it is assigned one of these personalities:

1.  **Tracker Bot (The "Gambler")**
    *   **Logic:** "This person hasn't been the Chor in a long time... surely it's their turn!"
    *   **How it works:** Tracks how many times each player has been Chor. It guesses the player who has been Chor the *least* often.
2.  **Hunter Bot (The "Competitor")**
    *   **Logic:** "I need to stop the winning player!"
    *   **How it works:** It checks the scoreboard and guesses the player with the *highest* current score.
3.  **Random Bot (The "Wildcard")**
    *   **Logic:** "I have no idea, picking randomly!"
    *   **How it works:** Picks a suspect purely at random.

## How to Play
1. The game assigns roles randomly.
2. **Sipahi** has to guess who the **Chor** is.
3. If Sipahi guesses correctly, they get 500 points.
4. If Sipahi guesses incorrectly, the Chor gets the Sipahi's points (500), and Sipahi gets 0!

## Installation
```bash
git clone git@github.com:jaygaha/raja-chor-mantri-sipahi.git
cd raja-chor-mantri-sipahi
```

## How to Run
```bash
python main.py
```

## Future Next Steps
- [x] **Phase 1:** Core Game Logic
- [x] **Phase 2:** Smarter Bot AI (Personalities)
- [ ] **Phase 3:** WebSocket server for multiplayer
- [ ] **Phase 4:** Web frontend interface

## Credits
Based on the traditional game "Raja Mantri Chor Sipahi".
- Wikipedia: https://en.wikipedia.org/wiki/Raja_Chor_Mantri_Sipahi