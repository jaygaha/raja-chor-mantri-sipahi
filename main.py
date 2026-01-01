"""
Raja Chor Mantri Sipahi Basic implementation
"""
import random
import os

# -- CONFIGURATION --
# Points for each role
POINTS_RAJA = 1000
POINTS_MANTRI = 800
POINTS_SIPAHI = 500
POINTS_CHOR = 0

def clear_screen():
    # Helper to clear the screen so players can't see each other's roles
    os.system('cls' if os.name == 'nt' else 'clear')

class Player:
    def __init__(self, name, is_bot=False):
        self.name = name
        self.is_bot = is_bot
        self.score = 0
        self.role = ""
        # Strategies: 'random', 'tracker', 'hunter'
        self.strategy = "random" 
        self.chor_count = 0  # Number of times this player has been Chor

def get_player_names():
    print("WELCOME TO RAJA CHOR MANTRI SIPAHI")
    print("----------------------------------")
    
    # input validation
    while True:
        try:
            num = int(input("How many humans are playing? (1-4): "))
            if num >= 1 and num <= 4:
                break
            print("Please enter a number between 1 and 4.")
        except:
            print("That's not a number!")

    players_list = []
    
    # Get names for humans
    for i in range(num):
        name = input("Enter name for Player " + str(i + 1) + ": ")
        new_player = Player(name)
        players_list.append(new_player)
    
    # Fill the rest with bots
    bots_needed = 4 - num
    strategies = ["random", "tracker", "hunter"]
    
    for i in range(bots_needed):
        bot_name = "Bot " + str(i + 1)
        
        # Assign a random personality to the bot
        bot_strategy = random.choice(strategies)
        
        print("Adding " + bot_name + " (" + bot_strategy + " personality)")
        
        new_player = Player(bot_name, is_bot=True)
        new_player.strategy = bot_strategy
        players_list.append(new_player)

    return players_list

def get_bot_guess(sipahi_bot, options):
    """
    Decide who to guess based on the bot's strategy.
    
    sipahi_bot: The Player object who is guessing
    options: List of Player objects who could be the Chor
    """
    strategy = sipahi_bot.strategy
    print(sipahi_bot.name + " is thinking... (Strategy: " + strategy + ")")
    
    guessed_player = None
    
    if strategy == "tracker":
        # Tracker Strategy: Guess the person who has been Chor the LEAST often.
        # Logic: "They haven't been Chor in a while, it must be their turn!" (Gambler's Fallacy)
        
        # Sort options by chor_count (lowest first)
        # We start with the first person as the best candidate
        best_candidate = options[0]
        for p in options:
            if p.chor_count < best_candidate.chor_count:
                best_candidate = p
        
        guessed_player = best_candidate
        
    elif strategy == "hunter":
        # Hunter Strategy: Guess the person with the HIGHEST score.
        # Logic: "I want to take down the leader!"
        
        # Sort options by score (highest first)
        best_candidate = options[0]
        for p in options:
            if p.score > best_candidate.score:
                best_candidate = p
                
        guessed_player = best_candidate
        
    else:
        # Random Strategy (or fallback)
        guessed_player = random.choice(options)
        
    return guessed_player

def play_game():
    players = get_player_names()
    
    # Ask for rounds
    try:
        total_rounds = int(input("How many rounds? (default 5): "))
    except:
        total_rounds = 5
        print("Using default 5 rounds.")

    print("\nStarting Game!")
    print("----------------")
    
    current_round = 1
    
    while current_round <= total_rounds:
        print("\n--- ROUND " + str(current_round) + " ---")
        
        # 1. Assign Roles
        # We need a list of roles to give out
        roles = ["Raja", "Mantri", "Sipahi", "Chor"]
        random.shuffle(roles)
        
        # Give one role to each player
        for i in range(4):
            players[i].role = roles[i]
            
        # 2. Show roles (secretly!)
        for p in players:
            if p.is_bot == False:
                print("\n" + p.name + ", it is your turn.")
                input("Press Enter to see your role (don't let others see!)...")
                print("YOU ARE: " + p.role)
                input("Press Enter to clear screen...")
                clear_screen()
        
        # 3. Find who is who
        sipahi = None
        chor = None
        
        for p in players:
            if p.role == "Sipahi":
                sipahi = p
            if p.role == "Chor":
                chor = p
                
        # 4. Sipahi guesses
        print("\n" + sipahi.name + " is the Sipahi!")
        print("Sipahi needs to find the Chor.")
        
        # Create a list of people Sipahi can guess (everyone except themselves)
        options = []
        for p in players:
            if p != sipahi:
                options.append(p)
        
        guessed_correctly = False
        
        # If Sipahi is a bot, uses its strategy
        if sipahi.is_bot:
            guessed_player = get_bot_guess(sipahi, options)
            print("Sipahi guesses: " + guessed_player.name)
            
            if guessed_player == chor:
                guessed_correctly = True
        else:
            # Human Sipahi guesses
            print("Who is the Chor?")
            for i in range(3):
                # options has 3 people. i goes 0, 1, 2. print 1, 2, 3
                print(str(i + 1) + ". " + options[i].name)
                
            choice = 0
            while True:
                try:
                    choice = int(input("Enter number (1-3): "))
                    if choice >= 1 and choice <= 3:
                        break
                except:
                    pass
                print("Please enter 1, 2, or 3")
            
            guessed_player = options[choice - 1]
            if guessed_player == chor:
                guessed_correctly = True

        # 5. Result
        print("\nRELVEALING ROLES:")
        for p in players:
            print(p.name + " was " + p.role)
            # Update chor_count history for 'tracker' bots
            if p.role == "Chor":
                p.chor_count += 1
            
        if guessed_correctly:
            print("\nCORRECT! Sipahi found the Chor.")
            # Everyone gets their own points
            for p in players:
                if p.role == "Raja":
                    p.score += POINTS_RAJA
                elif p.role == "Mantri":
                    p.score += POINTS_MANTRI
                elif p.role == "Sipahi":
                    p.score += POINTS_SIPAHI
                elif p.role == "Chor":
                    p.score += POINTS_CHOR
        else:
            print("\nWRONG! Sipahi guessed " + guessed_player.name + ".")
            print("Sipahi calculates swap with Chor!")
            # Swap Sipahi and Chor points
            for p in players:
                if p.role == "Raja":
                    p.score += POINTS_RAJA
                elif p.role == "Mantri":
                    p.score += POINTS_MANTRI
                elif p.role == "Sipahi":
                    p.score += 0 # Sipahi gets 0 (Chor points)
                elif p.role == "Chor":
                    p.score += POINTS_SIPAHI # Chor gets Sipahi points
        
        # Show scores
        print("\nSCOREBOARD:")
        for p in players:
            print(p.name + ": " + str(p.score))
            
        input("\nPress Enter only for next round...")
        clear_screen()
        current_round += 1

    # End of game
    print("\nGAME OVER!!")
    print("Final Scores:")
    # Find winner
    winner = players[0]
    for p in players:
        print(p.name + ": " + str(p.score))
        if p.score > winner.score:
            winner = p
            
    print("\nThe Winner is: " + winner.name)

if __name__ == "__main__":
    play_game()