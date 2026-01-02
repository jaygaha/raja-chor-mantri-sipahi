import asyncio
import websockets
import json
import random
from game.engine import GameEngine, Player

# Constants
PORT = 8765

class GameServer:
    def __init__(self):
        self.game = GameEngine()
        self.connected_clients = set()
        self.game_started = False
        
        # Game Settings (Defaults)
        self.required_humans = 4
        self.total_rounds = 5
        
        # Map: websocket -> asyncio.Future
        self.waiting_for_input = {}
        
    async def broadcast(self, message):
        """Send a JSON message to all connected clients"""
        # If nobody is connected, don't do anything
        if not self.connected_clients:
            return
            
        json_msg = json.dumps(message)
        tasks = []
        for ws in self.connected_clients:
            try:
                # Add the send task to our list
                tasks.append(ws.send(json_msg))
            except:
                pass 
        
        # Run all send tasks at the same time (async)
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def personal_message(self, websocket, message):
        """Send to one specific client"""
        try:
            await websocket.send(json.dumps(message))
        except:
            pass

    async def wait_for_input(self, websocket, timeout=30.0):
        """
        Wait for a message from a specific client.
        Uses a Future mechanism so logic can happen in `handler`.
        """
        # Get the current event loop
        loop = asyncio.get_running_loop()
        
        # Create a new "Future" (like a promise)
        future = loop.create_future()
        
        # Store it so the handler knows we are waiting
        self.waiting_for_input[websocket] = future
        
        try:
            # Wait until the future is done (or timeout)
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            # Clean up if timed out
            if websocket in self.waiting_for_input:
                del self.waiting_for_input[websocket]
            raise
        except Exception as e:
            # Clean up on error
            if websocket in self.waiting_for_input:
                del self.waiting_for_input[websocket]
            raise e

    async def handle_game_loop(self):
        """The main game loop running on the server"""
        print("Starting Game Loop...")
        self.game_started = True
        
        # 1. Fill empty slots with bots
        # This will add bots until we have 4 players total
        self.game.fill_with_bots()
        
        bot_count = sum(1 for p in self.game.players if p.is_bot)
        await self.broadcast({
            "type": "info", 
            "message": f"Game Starting! {bot_count} Bots added."
        })

        # 2. Loop through rounds
        # Use the number of rounds set by the Host
        for r in range(self.total_rounds):
            round_num = r + 1
            await self.broadcast({"type": "round_start", "round": round_num, "total": self.total_rounds})
            
            # Start Round Logic (Shuffle roles)
            self.game.start_round()
            
            # Send roles to players
            for player in self.game.players:
                if player.websocket:
                    await self.personal_message(player.websocket, {
                        "type": "role_reveal",
                        "role": player.role
                    })
            
            await asyncio.sleep(3)
            
            # Identify Sipahi and Chor Options
            sipahi = self.game.get_sipahi()
            chor_candidates = self.game.get_potential_chors(sipahi)
            chor_names = [p.name for p in chor_candidates]
            
            # Tell everyone who the Sipahi is
            await self.broadcast({
                "type": "sipahi_turn",
                "sipahi": sipahi.name,
                "chor_options": chor_names
            })
            
            guessed_player_name = None
            
            # 3. Get Sipahi's Guess
            if sipahi.is_bot:
                # Bot Logic
                await asyncio.sleep(2)
                guess = self.game.get_bot_guess(sipahi)
                guessed_player_name = guess.name
                await self.broadcast({"type": "info", "message": f"{sipahi.name} (Bot) is thinking..."})
                await asyncio.sleep(1)
            else:
                # Human Logic
                try:
                    await self.personal_message(sipahi.websocket, {
                        "type": "input_request",
                        "prompt": "choose_chor",
                        "title": "Who is the Chor?",
                        "options": chor_names
                    })
                    
                    # Wait for the player to reply
                    response_json = await self.wait_for_input(sipahi.websocket, timeout=30.0)
                    response = json.loads(response_json)
                    guessed_player_name = response.get("value")
                    
                except asyncio.TimeoutError:
                    await self.broadcast({"type": "info", "message": "Sipahi timed out! Choosing randomly."})
                    guess = random.choice(chor_candidates)
                    guessed_player_name = guess.name
                except Exception as e:
                    print(f"Error getting guess: {e}")
                    guess = random.choice(chor_candidates)
                    guessed_player_name = guess.name

            # 4. Process Result
            await self.broadcast({"type": "info", "message": f"{sipahi.name} guessed: {guessed_player_name}"})
            await asyncio.sleep(1)
            
            is_correct, score_updates = self.game.process_guess(sipahi, guessed_player_name)
            
            # Reveal Roles
            all_roles = self.game.get_role_info()
            await self.broadcast({
                "type": "round_end",
                "correct": is_correct,
                "all_roles": all_roles,
                "scores": score_updates
            })
            
            # Show Scoreboard
            scoreboard = {p.name: p.score for p in self.game.players}
            await self.broadcast({"type": "scoreboard", "scores": scoreboard})
            
            await asyncio.sleep(4)

        # 5. Game Over
        winner = max(self.game.players, key=lambda p: p.score)
        await self.broadcast({
            "type": "game_over",
            "winner": winner.name,
            "final_scores": {p.name: p.score for p in self.game.players}
        })
        
        print("Game Finished.")
        self.game_started = False
        self.game = GameEngine()
        self.connected_clients.clear()
        self.waiting_for_input.clear()
        # Reset defaults
        self.required_humans = 4
        self.total_rounds = 5

    async def register(self, websocket):
        """Handle new connections"""
        if self.game_started:
            await websocket.close(reason="Game already in progress")
            return

        print("New connection...")
        try:
            # We are here BEFORE the handler loop starts for this client.
            # So we can use `websocket.recv()` directly.
            
            # 1. Ask for Name
            await websocket.send(json.dumps({"type": "input_request", "prompt": "name"}))
            name_response = await websocket.recv()
            
            data = json.loads(name_response)
            player_name = data.get("value", "Unknown")
            
            # 2. Host Logic (First player configures the game)
            is_host = (len(self.game.players) == 0)
            
            if is_host:
                print(f"{player_name} is the HOST.")
                await self.personal_message(websocket, {
                    "type": "info", 
                    "message": "You are the HOST! Please configure the game."
                })
                
                # Ask: How many humans?
                await websocket.send(json.dumps({
                    "type": "input_request", 
                    "prompt": "choose_chor", 
                    "title": "How many humans?",
                    "options": ["1 Human", "2 Humans", "3 Humans", "4 Humans"] 
                }))
                
                # Wait for answer
                resp1 = await websocket.recv()
                data1 = json.loads(resp1)
                # The client sends the string value selected from options
                # e.g., "1 Human"
                choice_str = data1.get("value", "4 Humans")
                # Parse the number (first character)
                self.required_humans = int(choice_str.split()[0])
                
                await self.personal_message(websocket, {
                    "type": "info", 
                    "message": f"Set to {self.required_humans} human players."
                })

                # Ask: How many rounds?
                # We use the new "number_input" type for free input with limits
                await websocket.send(json.dumps({
                    "type": "input_request",
                    "prompt": "number_input",
                    "title": "How many rounds would you like to play?",
                    "min": 3,
                    "max": 20
                }))
                
                resp2 = await websocket.recv()
                data2 = json.loads(resp2)
                # Client guarantees it's a valid number between min and max
                self.total_rounds = data2.get("value", 5)
                
                await self.personal_message(websocket, {
                    "type": "info",
                    "message": f"Game set for {self.total_rounds} rounds!"
                })

            
            # Create Player
            new_player = Player(player_name, is_bot=False)
            new_player.websocket = websocket
            
            success = self.game.add_player(new_player)
            
            if success:
                self.connected_clients.add(websocket)
                current_count = len(self.game.players)
                print(f"Player joined: {player_name} ({current_count}/{self.required_humans})")
                
                await self.broadcast({
                    "type": "info", 
                    "message": f"{player_name} joined! ({current_count}/{self.required_humans})"
                })
                
                # Auto-start if we have enough humans
                if current_count >= self.required_humans:
                    print("Requirement met! Starting game...")
                    asyncio.create_task(self.handle_game_loop())
                else:
                    await self.personal_message(websocket, {
                        "type": "info",
                        "message": f"Waiting for {self.required_humans - current_count} more player(s)..."
                    })

            else:
                await websocket.send(json.dumps({"type": "error", "message": "Game Full"}))
                await websocket.close()
                return False
                
            return True 
                
        except Exception as e:
            print(f"Registration Error: {e}")
            return False

    async def handler(self, websocket):
        """Main WebSocket handler"""
        # 1. Register Phase (Exclusive read access)
        registered = await self.register(websocket)
        if not registered:
            return

        # 2. Main Loop (Shared read access via Futures)
        try:
            async for message in websocket:
                # Check if someone is waiting for input from this socket
                if websocket in self.waiting_for_input:
                    future = self.waiting_for_input.pop(websocket)
                    if not future.done():
                        future.set_result(message)
                    continue
                
                # Check commands
                try:
                    data = json.loads(message)
                    if data.get("type") == "command" and data.get("command") == "start":
                       if not self.game_started and len(self.game.players) > 0:
                           asyncio.create_task(self.handle_game_loop())
                except:
                    pass
                    
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            if websocket in self.connected_clients:
                self.connected_clients.remove(websocket)
                if websocket in self.waiting_for_input:
                    future = self.waiting_for_input.pop(websocket)
                    if not future.done():
                        future.set_exception(Exception("Client Disconnected"))

async def main():
    """Main server entry point"""
    server = GameServer()
    print(f"Raja Mantri Chor Sipahi Server")
    print(f"Starting on port {PORT}...")
    print(f"Connect via ws://localhost:{PORT}")

    async with websockets.serve(server.handler, "localhost", PORT):
        print(f"Server running! Waiting for players...")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nServer stopping...")
        print("Goodbye!\n")