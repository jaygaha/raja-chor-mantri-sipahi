import random

# -- CONFIGURATION --
POINTS_RAJA = 1000
POINTS_MANTRI = 800
POINTS_SIPAHI = 500
POINTS_CHOR = 0

class Player:
    def __init__(self, name, is_bot=False):
        self.name = name
        self.is_bot = is_bot
        self.score = 0
        self.role = ""
        self.strategy = "random" 
        self.chor_count = 0
        # WebSocket connection (None for bots)
        self.websocket = None

class GameEngine:
    def __init__(self):
        self.players = []
        self.current_round = 0
        self.total_rounds = 5
        self.roles = ["Raja", "Mantri", "Sipahi", "Chor"]
        
    def add_player(self, player):
        if len(self.players) < 4:
            self.players.append(player)
            return True
        return False
        
    def fill_with_bots(self):
        """Adds bots until there are 4 players"""
        strategies = ["random", "tracker", "hunter"]
        bots_needed = 4 - len(self.players)
        
        for i in range(bots_needed):
            bot_name = f"Bot_{i+1}"
            bot = Player(bot_name, is_bot=True)
            bot.strategy = random.choice(strategies)
            self.players.append(bot)
            
    def start_round(self):
        self.current_round += 1
        random.shuffle(self.roles)
        for i, player in enumerate(self.players):
            player.role = self.roles[i]
            
    def get_role_info(self):
        """Returns a dict of player_name -> role"""
        return {p.name: p.role for p in self.players}

    def get_sipahi(self):
        for p in self.players:
            if p.role == "Sipahi":
                return p
        return None

    def get_chor(self):
        for p in self.players:
            if p.role == "Chor":
                return p
        return None
        
    def get_potential_chors(self, sipahi):
        """Returns list of players who are NOT the Sipahi (Potential Chors)"""
        return [p for p in self.players if p != sipahi]

    def process_guess(self, sipahi, guessed_player_name):
        """
        Processes the Sipahi's guess and updates scores.
        Returns (is_correct, points_updates_dict)
        """
        chor = self.get_chor()
        
        # Find guessed player object
        guessed_player = None
        for p in self.players:
            if p.name == guessed_player_name:
                guessed_player = p
                break
                
        if not guessed_player:
            return False, {} # Should not happen

        # Update chor stats
        if chor:
            chor.chor_count += 1
            
        is_correct = (guessed_player == chor)
        
        # Calculate scores
        updates = {}
        for p in self.players:
            points = 0
            if is_correct:
                if p.role == "Raja": points = POINTS_RAJA
                elif p.role == "Mantri": points = POINTS_MANTRI
                elif p.role == "Sipahi": points = POINTS_SIPAHI
                elif p.role == "Chor": points = POINTS_CHOR
            else:
                # Wrong guess swap
                if p.role == "Raja": points = POINTS_RAJA
                elif p.role == "Mantri": points = POINTS_MANTRI
                elif p.role == "Sipahi": points = 0       # Swapped
                elif p.role == "Chor": points = POINTS_SIPAHI # Swapped
            
            p.score += points
            updates[p.name] = points
            
        return is_correct, updates

    def get_bot_guess(self, sipahi_bot):
        """Ai Logic for bot guessing"""
        options = self.get_potential_chors(sipahi_bot)
        strategy = sipahi_bot.strategy
        
        if strategy == "tracker":
            # Lowest chor count
            best = options[0]
            for p in options:
                if p.chor_count < best.chor_count:
                    best = p
            return best
            
        elif strategy == "hunter":
            # Highest score
            best = options[0]
            for p in options:
                if p.score > best.score:
                    best = p
            return best
            
        else:
            return random.choice(options)
