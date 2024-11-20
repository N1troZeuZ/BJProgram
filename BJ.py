import random
import os
import time

# Define card values and suits
values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
          '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}
suits = ['♥', '♦', '♣', '♠']

# Create and shuffle deck
deck = [(value, suit) for value in values.keys() for suit in suits]
random.shuffle(deck)

# ASCII card representation
def render_card(value, suit):
    if value == '10':
        return f"""
┌───────┐
│{value}     │
│   {suit}   │
│     {value}│
└───────┘
"""
    else:
        return f"""
┌───────┐
│{value}      │
│   {suit}   │
│      {value}│
└───────┘
"""

def render_hand(hand):
    cards = [render_card(value, suit) for value, suit in hand]
    card_lines = [card.split('\n') for card in cards]
    combined_lines = [''.join(line) for line in zip(*card_lines)]
    return '\n'.join(combined_lines)

# Clear screen for smooth updating
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def deal_card():
    return deck.pop()

def calculate_hand_value(hand):
    value = sum(values[card[0]] for card in hand)
    # Adjust for aces if total is over 21
    aces = sum(1 for card in hand if card[0] == 'A')
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

def hand_description(hand):
    value = calculate_hand_value(hand)
    aces = sum(1 for card in hand if card[0] == 'A')
    if len(hand) == 2 and value == 21:
        return "Natural Blackjack!"
    elif aces == 0:
        return "Hard Hand."
    elif aces > 0 and value <= 21:
        return "Soft Hand."
    else:
        return "Hand."

def play_blackjack():
    while True:
        # Initial deal
        player_hand = [deal_card(), deal_card()]
        dealer_hand = [deal_card(), deal_card()]

        # Player's turn
        while True:
            clear_screen()

            # Display hands
            print("Dealer's Hand:")
            print(render_hand([dealer_hand[0], ('?', '?')]))  # Hide one dealer card
            print("\nPlayer's Hand:")
            print(render_hand(player_hand))
            print(f"\n{hand_description(player_hand)}")

            # Player's action
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
        if calculate_hand_value(player_hand) <= 21:
            while calculate_hand_value(dealer_hand) < 17:
                dealer_hand.append(deal_card())
                time.sleep(1)  # Simulate dealer thinking
                clear_screen()
                print("Dealer's Hand:")
                print(render_hand(dealer_hand))
                print("\nPlayer's Hand:")
                print(render_hand(player_hand))
                print(f"\n{hand_description(player_hand)}")

        # Final result
        clear_screen()
        print("Dealer's Hand:")
        print(render_hand(dealer_hand))
        print(f"\n{hand_description(dealer_hand)}")
        print("\nPlayer's Hand:")
        print(render_hand(player_hand))
        print(f"\n{hand_description(player_hand)}")

        player_value = calculate_hand_value(player_hand)
        dealer_value = calculate_hand_value(dealer_hand)

        # Determine winner
        if player_value > 21:
            print("\nBust! You went over 21. Dealer wins.")
        elif dealer_value > 21:
            print("\nDealer busts! You win.")
        elif player_value > dealer_value:
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
