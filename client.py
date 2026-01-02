import asyncio
import websockets
import json
import os
from datetime import datetime

SERVER_URL = "ws://localhost:8765"

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    # Role colors
    RAJA = '\033[93m'      # Yellow/Gold
    MANTRI = '\033[95m'    # Magenta/Purple
    SIPAHI = '\033[91m'    # Red
    CHOR = '\033[90m'      # Dark Gray

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(text):
    """Print a styled header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.ENDC}\n")

def print_info(message):
    """Print an info message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{Colors.BLUE}[{timestamp}]{Colors.ENDC} {message}")

def print_success(message):
    """Print a success message"""
    print(f"{Colors.GREEN}✓{Colors.ENDC} {message}")

def print_error(message):
    """Print an error message"""
    print(f"{Colors.RED}✗ Error:{Colors.ENDC} {message}")

def print_role(role):
    """Print role with appropriate color"""
    color_map = {
        'Raja': Colors.RAJA,
        'Mantri': Colors.MANTRI,
        'Sipahi': Colors.SIPAHI,
        'Chor': Colors.CHOR
    }
    color = color_map.get(role, Colors.ENDC)
    print(f"\n{Colors.BOLD}{color}{'*'*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{color}{'YOUR ROLE:'.center(60)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{color}{role.center(60)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{color}{'*'*60}{Colors.ENDC}")
    print(f"{Colors.YELLOW}(Keep it secret! 🤫){Colors.ENDC}\n")

def print_divider():
    """Print a simple divider"""
    print(f"{Colors.CYAN}{'-'*60}{Colors.ENDC}")

async def connect():
    """Connect to the game server and handle messages"""
    print_header("Raja Mantri Chor Sipahi")
    print_info(f"Connecting to {SERVER_URL}...")
    
    try:
        async with websockets.connect(SERVER_URL) as websocket:
            print_success("Connected to server!")
            print_divider()
            
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    msg_type = data.get("type")
                    
                    # Handle different message types
                    if msg_type == "input_request":
                        prompt = data.get("prompt")
                        
                        if prompt == "name":
                            print()
                            user_input = input(f"{Colors.BOLD}Enter your name:{Colors.ENDC} ")
                            await websocket.send(json.dumps({"type": "response", "value": user_input}))
                            print_info("Waiting for other players...")
                            print_divider()
                            
                        elif prompt == "choose_chor":
                            options = data.get("options", [])
                            title = data.get("title", "Who is the Chor?")
                            
                            print(f"\n{Colors.BOLD}{Colors.YELLOW}{title}{Colors.ENDC}")
                            for i, name in enumerate(options, 1):
                                print(f"{Colors.CYAN}{i}.{Colors.ENDC} {name}")
                            
                            while True:
                                try:
                                    choice_input = input(f"\n{Colors.BOLD}Enter number (1-{len(options)}):{Colors.ENDC} ")
                                    choice = int(choice_input)
                                    if 1 <= choice <= len(options):
                                        selected = options[choice-1]
                                        await websocket.send(json.dumps({"type": "response", "value": selected}))
                                        print_divider()
                                        break
                                    else:
                                        print_error(f"Please enter a number between 1 and {len(options)}")
                                except ValueError:
                                    print_error("Please enter a valid number")

                        elif prompt == "number_input":
                            title = data.get("title", "Enter number:")
                            min_val = data.get("min")
                            max_val = data.get("max")
                            
                            print(f"\n{Colors.BOLD}{Colors.YELLOW}{title}{Colors.ENDC}")
                            if min_val is not None and max_val is not None:
                                print(f"{Colors.CYAN}Range: {min_val} - {max_val}{Colors.ENDC}")
                                
                            while True:
                                try:
                                    user_str = input(f"\n{Colors.BOLD}Enter number:{Colors.ENDC} ")
                                    val = int(user_str)
                                    
                                    if min_val is not None and val < min_val:
                                        print_error(f"Too low! Minimum is {min_val}")
                                        continue
                                    if max_val is not None and val > max_val:
                                        print_error(f"Too high! Maximum is {max_val}")
                                        continue
                                        
                                    await websocket.send(json.dumps({"type": "response", "value": val}))
                                    print_divider()
                                    break
                                except ValueError:
                                    print_error("Please enter a valid number")
                    
                    elif msg_type == "info":
                        print_info(data.get('message'))
                        
                    elif msg_type == "round_start":
                        round_num = data.get("round")
                        total = data.get("total")
                        clear_screen()
                        print_header(f"ROUND {round_num} / {total}")
                        
                    elif msg_type == "role_reveal":
                        role = data.get("role")
                        print_role(role)
                        
                    elif msg_type == "sipahi_turn":
                        sipahi = data.get("sipahi")
                        print(f"\n{Colors.BOLD}{Colors.RED}🔍 {sipahi} is the Sipahi!{Colors.ENDC}")
                        if "chor_options" in data:
                            chor_list = ", ".join(data['chor_options'])
                            print(f"{Colors.CYAN}Possible Chors: {chor_list}{Colors.ENDC}\n")
                        print_divider()
                            
                    elif msg_type == "round_end":
                        correct = data.get("correct")
                        roles = data.get("all_roles")
                        
                        # Build suspense
                        print("\n")
                        print_info("The Sipahi is making their guess...")
                        await asyncio.sleep(1)
                        print_info("...")
                        await asyncio.sleep(1)
                        
                        if correct:
                            print(f"\n{Colors.BOLD}{Colors.GREEN}✅ CORRECT!{Colors.ENDC}")
                            print(f"{Colors.GREEN}The Sipahi caught the Chor!{Colors.ENDC}\n")
                        else:
                            print(f"\n{Colors.BOLD}{Colors.RED}❌ WRONG!{Colors.ENDC}")
                            print(f"{Colors.RED}The Chor escaped!{Colors.ENDC}\n")
                        
                        await asyncio.sleep(1)
                        
                        print_divider()
                        print(f"{Colors.BOLD}ROLES REVEALED:{Colors.ENDC}\n")
                        
                        role_colors = {
                            'Raja': Colors.RAJA,
                            'Mantri': Colors.MANTRI,
                            'Sipahi': Colors.SIPAHI,
                            'Chor': Colors.CHOR
                        }
                        
                        for name, role in roles.items():
                            color = role_colors.get(role, Colors.ENDC)
                            print(f"  {color}{name}{Colors.ENDC}: {color}{role}{Colors.ENDC}")
                        print()
                        print_divider()
                            
                    elif msg_type == "scoreboard":
                        scores = data.get("scores")
                        print(f"\n{Colors.BOLD}{Colors.YELLOW}📊 SCOREBOARD{Colors.ENDC}\n")
                        
                        # Sort by score descending
                        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
                        
                        for rank, (name, score) in enumerate(sorted_scores, 1):
                            medal = ""
                            if rank == 1:
                                medal = "🥇"
                            elif rank == 2:
                                medal = "🥈"
                            elif rank == 3:
                                medal = "🥉"
                            else:
                                medal = "  "
                                
                            print(f"  {medal} {Colors.BOLD}{name}{Colors.ENDC}: {Colors.YELLOW}{score}{Colors.ENDC}")
                        
                        print()
                        print_divider()
                            
                    elif msg_type == "game_over":
                        winner = data.get("winner")
                        print("\n")
                        print_header("GAME OVER")
                        print(f"\n{Colors.BOLD}{Colors.YELLOW}🏆 WINNER: {winner} 🏆{Colors.ENDC}\n")
                        
                        # Final scores
                        final_scores = data.get("final_scores", {})
                        print(f"{Colors.BOLD}FINAL SCORES:{Colors.ENDC}\n")
                        
                        sorted_final = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
                        for rank, (name, score) in enumerate(sorted_final, 1):
                            medal = ""
                            if rank == 1:
                                medal = "🥇"
                            elif rank == 2:
                                medal = "🥈"
                            elif rank == 3:
                                medal = "🥉"
                            else:
                                medal = f"{rank}."
                                
                            print(f"  {medal} {Colors.BOLD}{name}{Colors.ENDC}: {Colors.YELLOW}{score}{Colors.ENDC}")
                        
                        print("\n")
                        print_divider()
                        print_info("Thanks for playing!")
                        return  # Exit game loop
                        
                    elif msg_type == "error":
                        print_error(data.get('message'))
                        return
                        
                except websockets.exceptions.ConnectionClosed:
                    print_error("Disconnected from server")
                    break
                except Exception as e:
                    print_error(f"Unexpected error: {e}")
                    break
                    
    except ConnectionRefusedError:
        print_error("Could not connect to server")
        print_info("Make sure the server is running on ws://localhost:8765")
    except Exception as e:
        print_error(f"Connection error: {e}")

def main():
    """Main entry point"""
    try:
        asyncio.run(connect())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Exiting game...{Colors.ENDC}")
        print_info("Goodbye! 👋\n")

if __name__ == "__main__":
    main()