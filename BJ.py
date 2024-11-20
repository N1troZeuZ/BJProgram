import random
import os
import time

# Define card values
values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
          '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}
suits = ['♥', '♦', '♣', '♠']

# Create deck
deck = [(value, suit) for value in values.keys() for suit in suits]

# ASCII card representation
def render_card(value, suit):
    return f"""
    ┌─────┐
    │{value:<2}   │
    │  {suit}  │
    │   {value:>2}│
    └─────┘

    """

def render_hand(hand):
    cards = [render_card(value, suit) for value, suit in hand]
    # Combine ASCII card rows into one display
    card_rows = [""] * 5
    for card in cards:
        card_lines = card.split("\n")
        for i in range(5):
            card_rows[i] += card_lines[i] + " "
    return "\n".join(card_rows)

# Clear screen for smooth updating
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def deal_card():
    return random.choice(deck)

def calculate_hand_value(hand):
    value = sum(values[card[0]] for card in hand)
    # Adjust for aces if total is over 21
    aces = sum(1 for card in hand if card[0] == 'A')
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

def play_blackjack():
    while True:
        # Initial deal
        player_hand = [deal_card(), deal_card()]
        dealer_hand = [deal_card(), deal_card()]

        # Game loop
        while True:
            clear_screen()

            # Display hands
            print("Dealer's Hand:")
            print(render_hand([dealer_hand[0], ('?', '?')]))  # Hide one dealer card
            print("\nPlayer's Hand:")
            print(render_hand(player_hand))

            # Player's turn
            move = input("Do you want to hit or stand? (h/s): ").strip().lower()
            if move == 'h':
                player_hand.append(deal_card())
                if calculate_hand_value(player_hand) > 21:
                    clear_screen()
                    print("Dealer's Hand:")
                    print(render_hand(dealer_hand))
                    print("\nPlayer's Hand:")
                    print(render_hand(player_hand))
                    print("\nBust! You went over 21. Dealer wins.")
                    break
            elif move == 's':
                break

        # Dealer's turn
        while calculate_hand_value(dealer_hand) < 12 or (
                12 <= calculate_hand_value(dealer_hand) < 17):
            dealer_hand.append(deal_card())
            time.sleep(1)  # Simulate dealer thinking
            clear_screen()
            print("Dealer's Hand:")
            print(render_hand(dealer_hand))
            print("\nPlayer's Hand:")
            print(render_hand(player_hand))

        # Final result
        clear_screen()
        print("Dealer's Hand:")
        print(render_hand(dealer_hand))
        print("\nPlayer's Hand:")
        print(render_hand(player_hand))

        player_value = calculate_hand_value(player_hand)
        dealer_value = calculate_hand_value(dealer_hand)

        if player_value > 21:
            print("\nBust! You went over 21. Dealer wins.")
        elif dealer_value > 21 or player_value > dealer_value:
            print("\nYou win!")
        elif player_value < dealer_value:
            print("\nDealer wins.")
        else:
            print("\nIt's a tie!")

        # Play again?
        play_again = input("\nWould you like to play again? (y/n): ").strip().lower()
        if play_again != 'y':
            print("Thanks for playing! Goodbye.")
            break

# Run the game
play_blackjack()
