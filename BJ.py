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
    def __init__(self, players=None):
        self.deck = Deck()
        self.players = players if players else []
        self.dealer = Hand()
        self.leaderboard = self.load_leaderboard()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def load_players(self):
        if os.path.exists(PLAYER_DATA_FILE):
            try:
                with open(PLAYER_DATA_FILE, 'r') as f:
                    saved_players = json.load(f)
                    # Reconstruct self.players with Hand objects
                    self.players = [{'name': name, 'balance': data['balance'], 'hand': Hand()} for name, data in saved_players.items()]
            except json.JSONDecodeError:
                print(Colors.RED + "Error: 'players.json' is corrupted or contains invalid JSON. Resetting player data." + Colors.END)
                self.players = []
                self.save_players()  # Overwrite the corrupted file with a fresh one
        else:
            self.players = []

    def save_players(self):
        # Create a dictionary to store only name and balance for each player
        saved_players = {player['name']: {'balance': player['balance']} for player in self.players}
        with open(PLAYER_DATA_FILE, 'w') as f:
            json.dump(saved_players, f, indent=4)

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

    def display_hands(self, hide_dealer_card=True):
        print(Colors.BLUE + "Dealer's Hand:" + Colors.END)
        print(self.dealer.render_hand(hide_first_card=hide_dealer_card))
        if hide_dealer_card:
            print("\n" + Colors.BLUE + "Player's Hands:" + Colors.END)
        else:
            print("\n" + Colors.GREEN + "Player's Hands:" + Colors.END)
        for player in self.players:
            print(f"{player['name']} ({Colors.YELLOW}Balance:{Colors.END} {render_money(player['balance'])})")
            print(player['hand'].render_hand())
            print(f"Value: {player['hand'].calculate_value()} - {player['hand'].description()}\n")

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
            while True:
                self.clear_screen()
                self.display_hands()
                print(f"{player['name']}'s Turn:")
                print(f"Balance: {render_money(player['balance'])}")
                # Ask for bet
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

                move = self.get_player_move(player)
                if move == 'h':
                    player['hand'].add_card(self.deck.deal_card())
                    if player['hand'].is_bust():
                        self.clear_screen()
                        self.display_hands()
                        print(Colors.RED + f"{player['name']} busts! Dealer wins." + Colors.END)
                        break
                elif move == 's':
                    break
                elif move == 'd':
                    if player['bet'] * 2 > player['balance']:
                        print(Colors.RED + "Insufficient balance to double down." + Colors.END)
                        continue
                    player['bet'] *= 2
                    player['balance'] -= player['bet'] / 2  # Deduct the additional bet
                    player['hand'].is_doubled = True
                    player['hand'].add_card(self.deck.deal_card())
                    print(Colors.CYAN + f"{player['name']} doubles down and receives one card." + Colors.END)
                    if player['hand'].is_bust():
                        self.clear_screen()
                        self.display_hands()
                        print(Colors.RED + f"{player['name']} busts after doubling down! Dealer wins." + Colors.END)
                    break

        # Dealer's turn
        if any(player['hand'].calculate_value() <= 21 for player in self.players):
            self.clear_screen()
            self.display_hands(hide_dealer_card=False)
            while self.dealer.calculate_value() < 17:
                time.sleep(1)  # Simulate dealer thinking
                self.dealer.add_card(self.deck.deal_card())
                self.clear_screen()
                self.display_hands(hide_dealer_card=False)

        dealer_value = self.dealer.calculate_value()
        dealer_bust = dealer_value > 21

        # Final results
        for player in self.players:
            player_value = player['hand'].calculate_value()
            bet = player.get('bet', 0)
            print(f"\n{player['name']}'s Result:")
            if player['hand'].is_bust():
                print(Colors.RED + "Bust! You lose your bet." + Colors.END)
            elif dealer_bust:
                winnings = bet * 2
                player['balance'] += winnings
                self.update_leaderboard(player['name'], winnings - bet)
                print(Colors.GREEN + f"Dealer busts! You win ${winnings}." + Colors.END)
            else:
                if player_value > dealer_value:
                    winnings = bet * 2
                    player['balance'] += winnings
                    self.update_leaderboard(player['name'], winnings - bet)
                    print(Colors.GREEN + f"You win! You receive ${winnings}." + Colors.END)
                elif player_value < dealer_value:
                    print(Colors.RED + "Dealer wins. You lose your bet." + Colors.END)
                else:
                    player['balance'] += bet
                    print(Colors.YELLOW + "It's a tie! Your bet is returned." + Colors.END)
            # Reset bet
            player.pop('bet', None)

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
            print(Colors.RED + f"{player['name']} has run out of balance and is removed from the game." + Colors.END)
            self.players.remove(player)
        return len(active_players) > 0

    def show_leaderboard(self):
        print(Colors.HEADER + "\n=== Leaderboard ===" + Colors.END)
        if not self.leaderboard:
            print("No entries yet.")
            return
        # Sort leaderboard
        sorted_leaderboard = sorted(self.leaderboard.items(), key=lambda x: x[1], reverse=True)
        for idx, (player, amount) in enumerate(sorted_leaderboard, start=1):
            print(f"{idx}. {player} - ${amount}")
        print()

    def select_players(self):
        self.load_players()  # Ensure self.players is loaded
        saved_players = {player['name']: {'balance': player['balance']} for player in self.players}  # Reconstruct saved_players
        if saved_players:
            print(Colors.HEADER + "=== Player Selection ===" + Colors.END)
            print("1. Select existing player")
            print("2. Create new player")
            print("3. Delete a player")
            print("4. View Leaderboard")
            choice = input("Choose an option (1-4): ").strip()
            if choice == '1':
                player_names = list(saved_players.keys())
                if not player_names:
                    print(Colors.RED + "No saved players found. Please create a new player." + Colors.END)
                    return self.create_new_player(saved_players)
                for idx, name in enumerate(player_names, start=1):
                    print(f"{idx}. {name} (Balance: ${saved_players[name]['balance']})")
                while True:
                    try:
                        selection = int(input(f"Select a player (1-{len(player_names)}): "))
                        if 1 <= selection <= len(player_names):
                            selected_name = player_names[selection - 1]
                            # Find the player in self.players
                            for player in self.players:
                                if player['name'] == selected_name:
                                    self.players.append({
                                        'name': selected_name,
                                        'balance': player['balance'],
                                        'hand': Hand()
                                    })
                                    break
                            print(Colors.GREEN + f"Player '{selected_name}' selected." + Colors.END)
                            return
                        else:
                            print(Colors.RED + "Invalid selection." + Colors.END)
                    except ValueError:
                        print(Colors.RED + "Please enter a valid number." + Colors.END)
            elif choice == '2':
                self.create_new_player(saved_players)
            elif choice == '3':
                self.delete_player(saved_players)
            elif choice == '4':
                self.show_leaderboard()
                self.select_players()  # Return to player selection after viewing leaderboard
            else:
                print(Colors.RED + "Invalid choice. Returning to main menu." + Colors.END)
                self.select_players()
        else:
            print(Colors.YELLOW + "No saved players found. Please create a new player." + Colors.END)
            self.create_new_player(saved_players)

    def create_new_player(self, saved_players):
        name = input("Enter a name for the new player: ").strip()
        if not name:
            name = f"Player{len(saved_players)+1}"
        if name in saved_players:
            print(Colors.RED + "Player with this name already exists." + Colors.END)
            self.create_new_player(saved_players)
            return
        saved_players[name] = {'balance': 1000}
        self.players.append({
            'name': name,
            'balance': 1000,
            'hand': Hand()
        })
        self.save_players()
        print(Colors.GREEN + f"Player '{name}' created and added to the game." + Colors.END)

    def delete_player(self, saved_players):
        player_names = list(saved_players.keys())
        if not player_names:
            print(Colors.RED + "No saved players to delete." + Colors.END)
            return
        for idx, name in enumerate(player_names, start=1):
            print(f"{idx}. {name} (Balance: ${saved_players[name]['balance']})")
        while True:
            try:
                selection = int(input(f"Select a player to delete (1-{len(player_names)}): "))
                if 1 <= selection <= len(player_names):
                    selected_name = player_names[selection - 1]
                    confirm = input(f"Are you sure you want to delete '{selected_name}'? (y/n): ").strip().lower()
                    if confirm == 'y':
                        del saved_players[selected_name]
                        # Remove the player from self.players if present
                        self.players = [p for p in self.players if p['name'] != selected_name]
                        self.save_players()
                        print(Colors.GREEN + f"Player '{selected_name}' deleted." + Colors.END)
                    else:
                        print("Deletion canceled.")
                    return
                else:
                    print(Colors.RED + "Invalid selection." + Colors.END)
            except ValueError:
                print(Colors.RED + "Please enter a valid number." + Colors.END)

    def start_game(self):
        while True:
            self.clear_screen()
            print(Colors.HEADER + "Welcome to Enhanced Blackjack!" + Colors.END)
            self.show_leaderboard()
            self.select_players()
            self.save_players()

            while True:
                if not self.check_balances():
                    print(Colors.YELLOW + "No players left with balance. Game over." + Colors.END)
                    break
                self.play_round()
                self.save_players()
                if not self.check_balances():
                    print(Colors.YELLOW + "No players left with balance. Game over." + Colors.END)
                    break
                play_again = input("\nWould you like to play another round? (y/n): ").strip().lower()
                if play_again != 'y':
                    print(Colors.HEADER + "Thanks for playing! Goodbye." + Colors.END)
                    self.save_leaderboard()
                    self.save_players()
                    sys.exit()

    def display_final_leaderboard(self):
        print(Colors.HEADER + "\n=== Final Leaderboard ===" + Colors.END)
        if not self.leaderboard:
            print("No entries yet.")
            return
        # Sort leaderboard
        sorted_leaderboard = sorted(self.leaderboard.items(), key=lambda x: x[1], reverse=True)
        for idx, (player, amount) in enumerate(sorted_leaderboard, start=1):
            print(f"{idx}. {player} - ${amount}")
        print()

# Run the game
if __name__ == "__main__":
    game = BlackjackGame()
    game.start_game()
