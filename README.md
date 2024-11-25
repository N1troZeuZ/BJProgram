# BJProgram
Black Jack Project With GUI
Details will be included at a later date program is still in early stages
REQUIRED TO RUN 
go to python/scripts folder, open a command window to this path, type the following:

C:\python34\scripts> python -m pip install pygame

Enhanced Blackjack Game
Welcome to the Enhanced Blackjack Game, a terminal-based Blackjack simulator with AI opponents inspired by the game "Papers, Please." This game offers an engaging and immersive experience with features like unique AI player names, background music, and dramatic narrative events for significant achievements.

Table of Contents
Features
Prerequisites
Installation
Setup
How to Play
Gameplay Mechanics
AI Players
Leaderboards
High Win Event
Troubleshooting
Contributing
License
Features
Standard Blackjack Mechanics: Hit, stand, and double down options.
Multiple Players: Play against multiple AI opponents with unique "Papers, Please" style names.
Persistent Data: Save player profiles, balances, and leaderboards across sessions.
Background Music: Enjoy ambient music during gameplay with a special victory track.
Dramatic Narrative Events: Experience a thrilling storyline when achieving significant wins.
ASCII Art Placeholders: Clean and clear interface with placeholders for visual elements.
Prerequisites
Before you begin, ensure you have met the following requirements:

Operating System: Windows, macOS, or Linux.
Python Version: Python 3.6 or higher.
Pygame Library: Required for background music playback.
Installation
Clone the Repository:

bash
Copy code
git clone https://github.com/N1troZeuZ/BJProgram
Navigate to the Project Directory:

How to Play
Run the Game:

Execute the BJ.py script using Python:

bash
Copy code
python BJ.py
Main Menu:

Upon launching, you'll be greeted with the main menu offering the following options:

markdown
Copy code
=== Main Menu ===
1. Select Existing Player
2. Create New Player
3. Add AI Players
4. Delete a Player
5. View Leaderboard
6. Start Game
7. Exit
Selecting or Creating a Player:

Select Existing Player: Choose from previously saved players.
Create New Player: Register a new player profile with an initial balance of $1,000.
Adding AI Players:

Add up to 5 AI opponents with unique "Papers, Please" style names. Each AI starts with a balance of $1,000.

Starting the Game:

Begin a new round of Blackjack. Follow on-screen prompts to place bets and make decisions during your turn.

Exiting the Game:

Save your progress and exit gracefully from the main menu.

Gameplay Mechanics
Betting:

Enter a bet amount within your current balance.
Player Actions:

Hit (h): Take another card.
Stand (s): End your turn.
Double Down (d): Double your bet, take one final card, and end your turn.
Winning Conditions:

Achieve a hand value higher than the dealer without exceeding $21.
Dealer busts (exceeds $21).
Natural Blackjack (an Ace and a 10-value card as your first two cards).
AI Players
Unique Names: AI opponents are assigned unique names from a predefined list inspired by "Papers, Please."
Behavior: AI players follow a simple strategy:
Hit if their hand value is below 17.
Stand otherwise.
Leaderboards
Track your earnings and see how you rank against other players. Leaderboards are updated based on the amount won during gameplay sessions.

High Win Event
Achieving a balance exceeding $10,000 triggers a dramatic narrative event:

Music Change: The background music switches to a victory track.
Narrative Sequence: A series of descriptive texts in red unfolds, enhancing the storytelling experience.
Player Deletion: The winning player is removed from the game.
Return to Main Menu: The game redirects back to the main menu, allowing you to select or create a new player.
Note: Ensure to keep track of your balance to experience this unique event.

Troubleshooting
Missing Music Files:
Ensure that background_music.mp3 and victory_music.mp3 are placed in the same directory as BJ.py.
Pygame Installation Issues:
Verify that pygame is installed correctly. Reinstall if necessary:

bash
Copy code
pip install pygame
JSON File Corruption:
If you encounter errors related to players.json, current_player.json, or leaderboard.json, delete the corrupted files and restart the game to generate fresh ones.