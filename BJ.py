import random

# Define card values
values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
          '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}

# Create deck
deck = list(values.keys()) * 4  # four of each card

def deal_card():
    return random.choice(deck)

def calculate_hand_value(hand):
    value = sum(values[card] for card in hand)
    # Adjust for aces if total is over 21
    aces = hand.count('A')
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

def display_hand(player, hand):
    print(f"{player} hand: {', '.join(hand)} (value: {calculate_hand_value(hand)})")

def play_blackjack():
    # Initial deal
    player_hand = [deal_card(), deal_card()]
    dealer_hand = [deal_card(), deal_card()]

    print("Welcome to Blackjack!")
    display_hand("Player", player_hand)
    print(f"Dealer shows: {dealer_hand[0]}")

    # Player turn
    while calculate_hand_value(player_hand) < 21:
        move = input("Do you want to hit or stand? (h/s): ").strip().lower()
        if move == 'h':
            player_hand.append(deal_card())
            display_hand("Player", player_hand)
            if calculate_hand_value(player_hand) > 21:
                print("Bust! You went over 21. Dealer wins.")
                return
        elif move == 's':
            break
        else:
            print("Invalid input. Please enter 'h' or 's'.")

    # Dealer turn
    while calculate_hand_value(dealer_hand) < 17:
        dealer_hand.append(deal_card())

    display_hand("Dealer", dealer_hand)

    # Determine winner
    player_value = calculate_hand_value(player_hand)
    dealer_value = calculate_hand_value(dealer_hand)

    if dealer_value > 21:
        print("Dealer busts! You win.")
    elif player_value > dealer_value:
        print("You win!")
    elif player_value < dealer_value:
        print("Dealer wins.")
    else:
        print("It's a tie!")

# Run the game
play_blackjack()
