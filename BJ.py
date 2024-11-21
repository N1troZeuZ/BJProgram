import random
import os
import time
import sys
import json

# ANSI escape codes for colored output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    END = '\033[0m'

# Define card values and suits
VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
    '8': 8, '9': 9, '10': 10, 'J': 10,
    'Q': 10, 'K': 10, 'A': 11
}
SUITS = ['♥', '♦', '♣', '♠']

# File paths for saving data
PLAYER_DATA_FILE = 'players.json'
CURRENT_PLAYER_FILE = 'current_player.json'
LEADERBOARD_FILE = 'leaderboard.json'

# Card class
class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

    def __str__(self):
        return f"{self.value}{self.suit}"

    def render(self):
        val = self.value
        suit = self.suit
        if val == '10':
            return f"""
    ┌───────┐
    │{val}     │
    │   {suit}   │
    │     {val}│
    └───────┘
        """
        else:
            return f"""
    ┌───────┐
    │{val}      │
    │   {suit}   │
    │      {val}│
    └───────┘
        """

# ASCII representation of money
def render_money(amount):
    lines = [
        " _____________________ ",
        "/                     \\",
        f"|        ${amount:<7}       |",
        "\\_____________________/"
    ]
    return '\n'.join(lines)

# ASCII Joker Card
def render_joker_card():
    joker = """
      _____
    /     \\
   | () () |
    \\  ^  /
     |||||
     |||||
    """
    play_again = "Play Again?"
    return f"{joker}\n{play_again.center(len(joker.splitlines()[0]))}"

# Deck class
class Deck:
    def __init__(self):
        self.cards = [Card(value, suit) for value in VALUES.keys() for suit in SUITS]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal_card(self):
        if len(self.cards) == 0:
            self.__init__()  # Reinitialize and shuffle if deck is empty
            print(Colors.YELLOW + "\nDeck is reshuffled." + Colors.END)
            time.sleep(1.5)  # Increased delay for readability
        return self.cards.pop()

    def cards_left(self):
        return len(self.cards)

# Hand class
class Hand:
    def __init__(self):
        self.cards = []
        self.is_doubled = False  # Track if the hand has been doubled down

    def add_card(self, card):
        self.cards.append(card)

    def calculate_value(self):
        value = sum(VALUES[card.value] for card in self.cards)
        # Adjust for aces if total is over 21
        aces = sum(1 for card in self.cards if card.value == 'A')
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    def description(self):
        value = self.calculate_value()
        aces = sum(1 for card in self.cards if card.value == 'A')
        if len(self.cards) == 2 and value == 21:
            return Colors.GREEN + "Natural Blackjack!" + Colors.END
        elif aces == 0:
            return "Hard Hand."
        elif aces > 0 and value <= 21:
            return "Soft Hand."
        else:
            return "Hand."

    def render_hand(self, hide_first_card=False):
        if hide_first_card:
            rendered_cards = [self.cards[0].render(), Card('?', '?').render()]
        else:
            rendered_cards = [card.render() for card in self.cards]
        card_lines = [card.split('\n') for card in rendered_cards]
        combined_lines = [''.join(line) for line in zip(*card_lines)]
        return '\n'.join(combined_lines)

    def is_bust(self):
        return self.calculate_value() > 21

# BlackjackGame class
class BlackjackGame:
    def __init__(self):
        self.deck = Deck()
        self.players = []  # Active players (one human, multiple AI)
        self.leaderboard = self.load_leaderboard()
        self.ai_player_count = 0  # To generate unique AI player names
        self.current_player_name = self.load_current_player()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def load_players(self):
        if os.path.exists(PLAYER_DATA_FILE):
            try:
                with open(PLAYER_DATA_FILE, 'r') as f:
                    saved_players = json.load(f)
                    # Return saved players as a dictionary
                    return saved_players
            except json.JSONDecodeError:
                print(Colors.RED + "Error: 'players.json' is corrupted or contains invalid JSON. Resetting player data." + Colors.END)
                return {}
        else:
            return {}

    def save_players_to_file(self, players_data):
        with open(PLAYER_DATA_FILE, 'w') as f:
            json.dump(players_data, f, indent=4)

    def load_current_player(self):
        if os.path.exists(CURRENT_PLAYER_FILE):
            try:
                with open(CURRENT_PLAYER_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get('current_player')
            except json.JSONDecodeError:
                print(Colors.RED + "Error: 'current_player.json' is corrupted or contains invalid JSON. Resetting current player." + Colors.END)
                return None
        else:
            return None

    def save_current_player(self, player_name):
        with open(CURRENT_PLAYER_FILE, 'w') as f:
            json.dump({'current_player': player_name}, f, indent=4)
        self.current_player_name = player_name  # Update the attribute immediately

    def load_leaderboard(self):
        if os.path.exists(LEADERBOARD_FILE):
            try:
                with open(LEADERBOARD_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(Colors.RED + "Error: 'leaderboard.json' is corrupted or contains invalid JSON. Resetting leaderboard data." + Colors.END)
                return {}
        return {}

    def save_leaderboard(self):
        with open(LEADERBOARD_FILE, 'w') as f:
            json.dump(self.leaderboard, f, indent=4)

    def get_player_move(self, player):
        if player.get('is_ai', False):
            # Simple AI logic: hit if value < 17, else stand
            value = player['hand'].calculate_value()
            if value < 17:
                move = 'h'
                print(Colors.MAGENTA + f"{player['name']} chooses to hit." + Colors.END)
            else:
                move = 's'
                print(Colors.MAGENTA + f"{player['name']} chooses to stand." + Colors.END)
            time.sleep(1.5)  # Increased delay for readability
            return move
        else:
            while True:
                move = input(f"{player['name']}, do you want to hit, stand, or double down? (h/s/d): ").strip().lower()
                if move in ['h', 's', 'd']:
                    # If player has already doubled down, they can't double again
                    if move == 'd' and (player['hand'].is_doubled or player['bet'] * 2 > player['balance']):
                        print(Colors.RED + "Cannot double down." + Colors.END)
                    else:
                        return move
                else:
                    print(Colors.RED + "Invalid input. Please enter 'h' to hit, 's' to stand, or 'd' to double down." + Colors.END)

    def display_player_hand(self, player, hide_dealer_card=True):
        self.clear_screen()
        print(Colors.BLUE + "Dealer's Hand:" + Colors.END)
        print(self.dealer.render_hand(hide_first_card=hide_dealer_card))
        print("\n" + Colors.YELLOW + f"{player['name']}'s Hand:" + Colors.END)
        print(f"Balance:\n{render_money(player['balance'])}")
        print(player['hand'].render_hand())
        print(f"Value: {player['hand'].calculate_value()} - {player['hand'].description()}\n")

    def display_result(self, player, dealer_value, dealer_bust):
        self.clear_screen()
        print(f"{player['name']}'s Result:")
        if player['hand'].is_bust():
            print(Colors.RED + "Bust! You lose your bet." + Colors.END)
        elif dealer_bust:
            winnings = player['bet'] * 2
            player['balance'] += winnings
            self.update_leaderboard(player['name'], winnings - player['bet'])
            print(Colors.GREEN + f"Dealer busts! You win ${winnings}." + Colors.END)
        else:
            player_value = player['hand'].calculate_value()
            if player_value > dealer_value:
                winnings = player['bet'] * 2
                player['balance'] += winnings
                self.update_leaderboard(player['name'], winnings - player['bet'])
                print(Colors.GREEN + f"You win! You receive ${winnings}." + Colors.END)
            elif player_value < dealer_value:
                print(Colors.RED + "Dealer wins. You lose your bet." + Colors.END)
            else:
                player['balance'] += player['bet']
                print(Colors.YELLOW + "It's a tie! Your bet is returned." + Colors.END)
        time.sleep(2)  # Increased delay for readability

    def display_joker_card(self):
        self.clear_screen()
        print(render_joker_card())
        while True:
            choice = input("Would you like to play again? (y/n): ").strip().lower()
            if choice == 'y':
                return True
            elif choice == 'n':
                return False
            else:
                print(Colors.RED + "Invalid input. Please enter 'y' or 'n'." + Colors.END)

    def play_round(self):
        # Initial deal
        for player in self.players:
            player['hand'] = Hand()
            player['hand'].add_card(self.deck.deal_card())
            player['hand'].add_card(self.deck.deal_card())
        self.dealer = Hand()
        self.dealer.add_card(self.deck.deal_card())
        self.dealer.add_card(self.deck.deal_card())

        # Players' turns
        for player in self.players:
            self.display_player_hand(player)
            if not player.get('is_ai', False):
                # Human player
                if 'bet' not in player:
                    while True:
                        try:
                            bet = float(input(f"{player['name']}, enter your bet: $"))
                            if 0 < bet <= player['balance']:
                                player['bet'] = bet
                                player['balance'] -= bet
                                break
                            else:
                                print(Colors.RED + "Invalid bet amount." + Colors.END)
                        except ValueError:
                            print(Colors.RED + "Please enter a valid number." + Colors.END)
            else:
                # AI player
                if 'bet' not in player:
                    bet = min(100, player['balance']) if player['balance'] >= 100 else player['balance']
                    player['bet'] = bet
                    player['balance'] -= bet
                    print(Colors.CYAN + f"{player['name']} places a bet of ${bet}." + Colors.END)
                    time.sleep(1.5)  # Increased delay

            # Player's actions
            while True:
                move = self.get_player_move(player)
                if move == 'h':
                    player['hand'].add_card(self.deck.deal_card())
                    self.display_player_hand(player)
                    if player['hand'].is_bust():
                        print(Colors.RED + f"{player['name']} busts! Dealer wins." + Colors.END)
                        time.sleep(2)  # Increased delay
                        break
                elif move == 's':
                    break
                elif move == 'd':
                    if player['bet'] * 2 > player['balance']:
                        print(Colors.RED + "Insufficient balance to double down." + Colors.END)
                        time.sleep(1.5)  # Increased delay
                        continue
                    player['bet'] *= 2
                    player['balance'] -= player['bet'] / 2  # Deduct the additional bet
                    player['hand'].is_doubled = True
                    player['hand'].add_card(self.deck.deal_card())
                    self.display_player_hand(player)
                    print(Colors.CYAN + f"{player['name']} doubles down and receives one card." + Colors.END)
                    time.sleep(1.5)  # Increased delay
                    if player['hand'].is_bust():
                        print(Colors.RED + f"{player['name']} busts after doubling down! Dealer wins." + Colors.END)
                        time.sleep(2)  # Increased delay
                    break

        # Dealer's turn
        # Check if any player hasn't busted
        if any(not player['hand'].is_bust() for player in self.players):
            self.clear_screen()
            print(Colors.BLUE + "Dealer's Turn:" + Colors.END)
            print("Dealer's Hand:")
            print(self.dealer.render_hand(hide_first_card=False))
            time.sleep(1.5)  # Increased delay
            while self.dealer.calculate_value() < 17:
                print(Colors.BLUE + "Dealer hits." + Colors.END)
                self.dealer.add_card(self.deck.deal_card())
                print("Dealer's Hand:")
                print(self.dealer.render_hand(hide_first_card=False))
                time.sleep(1.5)  # Increased delay
            if self.dealer.calculate_value() >= 17:
                print(Colors.BLUE + "Dealer stands." + Colors.END)
                time.sleep(1.5)  # Increased delay

        dealer_value = self.dealer.calculate_value()
        dealer_bust = dealer_value > 21

        # Display results for each player one at a time
        for player in self.players:
            self.display_result(player, dealer_value, dealer_bust)

        # Reset all players' bets for the next round
        for player in self.players:
            player.pop('bet', None)

        # Display ASCII Joker card and prompt to play again
        play_again = self.display_joker_card()
        return play_again  # Return the choice to the game loop

    def update_leaderboard(self, player_name, amount_won):
        if player_name in self.leaderboard:
            self.leaderboard[player_name] += amount_won
        else:
            self.leaderboard[player_name] = amount_won
        self.save_leaderboard()

    def check_balances(self):
        active_players = [player for player in self.players if player['balance'] > 0]
        eliminated = [player for player in self.players if player['balance'] <= 0]
        for player in eliminated:
            if player.get('is_ai', False):
                print(Colors.RED + f"{player['name']} (AI) has run out of balance and is removed from the game." + Colors.END)
            else:
                print(Colors.RED + f"{player['name']} has run out of balance and is removed from the game." + Colors.END)
            self.players.remove(player)
            time.sleep(1.5)  # Increased delay
        return len(active_players) > 0

    def show_leaderboard(self):
        self.clear_screen()
        print(Colors.HEADER + "\n=== Leaderboard ===" + Colors.END)
        if not self.leaderboard:
            print("No entries yet.")
        else:
            # Sort leaderboard
            sorted_leaderboard = sorted(self.leaderboard.items(), key=lambda x: x[1], reverse=True)
            for idx, (player, amount) in enumerate(sorted_leaderboard, start=1):
                print(f"{idx}. {player} - ${amount}")
        print()
        input("Press Enter to return to the main menu...")

    def select_players(self):
        while True:
            self.clear_screen()
            print(Colors.HEADER + "=== Main Menu ===" + Colors.END)
            print("1. Select Existing Player")
            print("2. Create New Player")
            print("3. Add AI Players")
            print("4. Delete a Player")
            print("5. View Leaderboard")
            print("6. Start Game")
            print("7. Exit")
            choice = input("Choose an option (1-7): ").strip()
            if choice == '1':
                self.select_existing_player()
            elif choice == '2':
                self.create_new_player()
            elif choice == '3':
                self.add_ai_players()
            elif choice == '4':
                self.delete_player()
            elif choice == '5':
                self.show_leaderboard()
            elif choice == '6':
                if self.current_player_name:
                    # Load current player details
                    players_data = self.load_players()
                    if self.current_player_name in players_data:
                        # Update the player's balance in self.players list
                        # Remove existing active human player if any
                        self.players = [p for p in self.players if p.get('is_ai', False)]
                        self.players.append({
                            'name': self.current_player_name,
                            'balance': players_data[self.current_player_name]['balance'],
                            'hand': Hand(),
                            'is_ai': False
                        })
                        return  # Proceed to start the game
                    else:
                        print(Colors.RED + "Current player not found. Please select or create a new player." + Colors.END)
                        time.sleep(2)  # Increased delay
                else:
                    print(Colors.RED + "No active human player found. Please select or create a player." + Colors.END)
                    time.sleep(2)  # Increased delay
            elif choice == '7':
                print(Colors.HEADER + "Thanks for playing! Goodbye." + Colors.END)
                self.save_leaderboard()
                # Update players.json with current players' balances
                players_data = self.load_players()
                for player in self.players:
                    if not player.get('is_ai', False):
                        players_data[player['name']]['balance'] = player['balance']
                self.save_players_to_file(players_data)
                self.save_current_player(None)
                time.sleep(2)  # Increased delay
                sys.exit()
            else:
                print(Colors.RED + "Invalid choice. Please select a valid option." + Colors.END)
                time.sleep(1.5)  # Increased delay

    def select_existing_player(self):
        saved_players = self.load_players()
        if not saved_players:
            print(Colors.RED + "No saved players found. Please create a new player." + Colors.END)
            time.sleep(2)  # Increased delay
            return
        player_names = list(saved_players.keys())
        self.clear_screen()
        print(Colors.HEADER + "=== Select Existing Player ===" + Colors.END)
        for idx, name in enumerate(player_names, start=1):
            print(f"{idx}. {name} (Balance: ${saved_players[name]['balance']})")
        while True:
            try:
                selection = int(input(f"Select a player to activate (1-{len(player_names)}): "))
                if 1 <= selection <= len(player_names):
                    selected_name = player_names[selection - 1]
                    # Set as current player
                    self.save_current_player(selected_name)
                    print(Colors.GREEN + f"Player '{selected_name}' is now the active player." + Colors.END)
                    time.sleep(1.5)  # Increased delay
                    return
                else:
                    print(Colors.RED + "Invalid selection." + Colors.END)
            except ValueError:
                print(Colors.RED + "Please enter a valid number." + Colors.END)

    def create_new_player(self):
        saved_players = self.load_players()
        while True:
            self.clear_screen()
            print(Colors.HEADER + "=== Create New Player ===" + Colors.END)
            name = input("Enter a name for the new player: ").strip()
            if not name:
                print(Colors.RED + "Name cannot be empty." + Colors.END)
                time.sleep(1.5)  # Increased delay
                continue
            if name in saved_players:
                print(Colors.RED + "Player with this name already exists." + Colors.END)
                time.sleep(1.5)  # Increased delay
                continue
            # Add new player to saved_players
            saved_players[name] = {'balance': 1000}
            self.save_players_to_file(saved_players)
            # Set as current player
            self.save_current_player(name)
            print(Colors.GREEN + f"Player '{name}' created and set as the active player with a balance of $1000." + Colors.END)
            time.sleep(2)  # Increased delay
            return

    def add_ai_players(self):
        while True:
            self.clear_screen()
            print(Colors.HEADER + "=== Add AI Players ===" + Colors.END)
            try:
                num_ai = int(input("Enter the number of AI players to add (1-5): "))
                if 1 <= num_ai <= 5:
                    break
                else:
                    print(Colors.RED + "Please enter a number between 1 and 5." + Colors.END)
                    time.sleep(1.5)  # Increased delay
            except ValueError:
                print(Colors.RED + "Please enter a valid number." + Colors.END)
                time.sleep(1.5)  # Increased delay
        for _ in range(num_ai):
            self.ai_player_count += 1
            ai_name = f"AI_Player_{self.ai_player_count}"
            # Ensure unique AI player names
            while any(player['name'] == ai_name for player in self.players):
                self.ai_player_count += 1
                ai_name = f"AI_Player_{self.ai_player_count}"
            self.players.append({
                'name': ai_name,
                'balance': 1000,  # AI players start with a balance of $1000
                'hand': Hand(),
                'is_ai': True
            })
            print(Colors.CYAN + f"AI Player '{ai_name}' added to the game with a balance of $1000." + Colors.END)
            time.sleep(0.5)
        print(Colors.GREEN + f"Added {num_ai} AI player(s)." + Colors.END)
        time.sleep(2)  # Increased delay

    def delete_player(self):
        saved_players = self.load_players()
        if not saved_players:
            print(Colors.RED + "No saved human players to delete." + Colors.END)
            time.sleep(2)  # Increased delay
            return
        player_names = list(saved_players.keys())
        self.clear_screen()
        print(Colors.HEADER + "=== Delete a Player ===" + Colors.END)
        for idx, name in enumerate(player_names, start=1):
            print(f"{idx}. {name} (Balance: ${saved_players[name]['balance']})")
        while True:
            try:
                selection = int(input(f"Select a player to delete (1-{len(player_names)}): "))
                if 1 <= selection <= len(player_names):
                    selected_name = player_names[selection - 1]
                    confirm = input(f"Are you sure you want to delete '{selected_name}'? (y/n): ").strip().lower()
                    if confirm == 'y':
                        # Remove from saved_players
                        del saved_players[selected_name]
                        self.save_players_to_file(saved_players)
                        # If the deleted player was the current player, unset current player
                        if self.current_player_name == selected_name:
                            self.save_current_player(None)
                            print(Colors.YELLOW + f"Deleted current active player '{selected_name}'. No active player now." + Colors.END)
                        else:
                            print(Colors.GREEN + f"Player '{selected_name}' deleted." + Colors.END)
                        time.sleep(2)  # Increased delay
                        return
                    else:
                        print("Deletion canceled.")
                        time.sleep(1.5)  # Increased delay
                        return
                else:
                    print(Colors.RED + "Invalid selection." + Colors.END)
            except ValueError:
                print(Colors.RED + "Please enter a valid number." + Colors.END)

    def start_game(self):
        while True:
            self.clear_screen()
            print(Colors.HEADER + "Welcome to Enhanced Blackjack with AI Players!" + Colors.END)
            self.show_leaderboard()
            self.select_players()
            # At this point, players list has the current human player and any AI players

            while True:
                self.clear_screen()
                print(Colors.HEADER + "=== Starting a New Round ===" + Colors.END)
                if not self.check_balances():
                    print(Colors.YELLOW + "No players left with balance. Game over." + Colors.END)
                    time.sleep(2)  # Increased delay
                    break
                play_again = self.play_round()
                # Update players.json with current players' balances
                players_data = self.load_players()
                for player in self.players:
                    if not player.get('is_ai', False):
                        players_data[player['name']]['balance'] = player['balance']
                self.save_players_to_file(players_data)
                self.save_current_player(self.current_player_name)
                self.save_leaderboard()
                if not self.check_balances():
                    print(Colors.YELLOW + "No players left with balance. Game over." + Colors.END)
                    time.sleep(2)  # Increased delay
                    break
                if not play_again:
                    # User chose not to play again; return to main menu
                    break
                # Else, continue to next round

            # After game over or choosing not to play again, return to main menu
            print(Colors.YELLOW + "Returning to main menu..." + Colors.END)
            time.sleep(2)  # Increased delay

    def display_final_leaderboard(self):
        self.clear_screen()
        print(Colors.HEADER + "\n=== Final Leaderboard ===" + Colors.END)
        if not self.leaderboard:
            print("No entries yet.")
        else:
            # Sort leaderboard
            sorted_leaderboard = sorted(self.leaderboard.items(), key=lambda x: x[1], reverse=True)
            for idx, (player, amount) in enumerate(sorted_leaderboard, start=1):
                print(f"{idx}. {player} - ${amount}")
        print()
        input("Press Enter to return to the main menu...")

# Run the game
if __name__ == "__main__":
    game = BlackjackGame()
    game.start_game()
