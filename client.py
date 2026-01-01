import asyncio
import websockets
import json
import os

SERVER_URL = "ws://localhost:8765"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

async def connect():
    print(f"Connecting to {SERVER_URL}...")
    try:
        async with websockets.connect(SERVER_URL) as websocket:
            print("Connected!")
            
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    msg_type = data.get("type")
                    
                    if msg_type == "input_request":
                        prompt = data.get("prompt")
                        
                        if prompt == "name":
                            user_input = input("\nEnter your name: ")
                            await websocket.send(json.dumps({"type": "response", "value": user_input}))
                            print("Waiting for players...")
                            
                        elif prompt == "choose_chor":
                            options = data.get("options", [])
                            title = data.get("title", "Who is the Chor?")
                            print(f"\n{title}")
                            for i, name in enumerate(options):
                                print(f"{i+1}. {name}")
                            
                            while True:
                                try:
                                    choice = int(input("Enter number: "))
                                    if 1 <= choice <= len(options):
                                        selected = options[choice-1]
                                        await websocket.send(json.dumps({"type": "response", "value": selected}))
                                        break
                                except ValueError:
                                    pass
                                print("Invalid choice.")

                        elif prompt == "number_input":
                            title = data.get("title", "Enter number:")
                            min_val = data.get("min")
                            max_val = data.get("max")
                            
                            print(f"\n{title}")
                            if min_val is not None and max_val is not None:
                                print(f"(Min: {min_val}, Max: {max_val})")
                                
                            while True:
                                try:
                                    user_str = input("> ")
                                    val = int(user_str)
                                    
                                    if min_val is not None and val < min_val:
                                        print(f"Too low! Minimum is {min_val}.")
                                        continue
                                    if max_val is not None and val > max_val:
                                        print(f"Too high! Maximum is {max_val}.")
                                        continue
                                        
                                    await websocket.send(json.dumps({"type": "response", "value": val}))
                                    break
                                except ValueError:
                                    print("Please enter a valid number.")
                    
                    elif msg_type == "info":
                        print(f"[INFO] {data.get('message')}")
                        
                    elif msg_type == "round_start":
                        round_num = data.get("round")
                        total = data.get("total")
                        clear_screen()
                        print(f"\n--- ROUND {round_num}/{total} ---")
                        
                    elif msg_type == "role_reveal":
                        role = data.get("role")
                        print(f"\nYour Role: {role}")
                        print("(Shhh! Keep it secret)")
                        
                    elif msg_type == "sipahi_turn":
                        sipahi = data.get("sipahi")
                        print(f"\n{sipahi} is the Sipahi!")
                        if "chor_options" in data:
                            print(f"Chor Options: {', '.join(data['chor_options'])}")

                            
                    elif msg_type == "round_end":
                        correct = data.get("correct")
                        roles = data.get("all_roles")
                        
                        # Suspense!
                        print("\nThe Sipahi guessed...")
                        await asyncio.sleep(1)
                        print("...")
                        await asyncio.sleep(1)
                        
                        if correct:
                            print("✅ CORRECT! The Sipahi caught the Chor!")
                        else:
                            print("❌ WRONG! The Chor got away!")
                        
                        await asyncio.sleep(1)
                        
                        print("\nROUND OVER!")
                        print("Roles:")
                        for name, role in roles.items():
                            emoji = "✅" if correct else "❌"
                            print(f"  {name}: {role}")
                            
                    elif msg_type == "scoreboard":
                        scores = data.get("scores")
                        print("\nSCOREBOARD:")
                        # Sort by score
                        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
                        for name, score in sorted_scores:
                            print(f"  {name}: {score}")
                            
                    elif msg_type == "game_over":
                        winner = data.get("winner")
                        print(f"\nGAME OVER! Winner is {winner}")
                        return # Exit loop
                        
                    elif msg_type == "error":
                        print(f"Error: {data.get('message')}")
                        return
                        
                except websockets.exceptions.ConnectionClosed:
                    print("Disconnected from server.")
                    break
                    
    except ConnectionRefusedError:
        print("Could not connect to server. Is it running?")

if __name__ == "__main__":
    try:
        asyncio.run(connect())
    except KeyboardInterrupt:
        print("\nExiting...")
