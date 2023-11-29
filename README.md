# Plunder-Game-with-Online_Multiplayer
Plunder is a card/board game that I adopted to a video game. It is setup to be played online via a custom coded server and network.

Intro: I had 3 goals for this project; learn object-oriented programing, learn how servers & networks work/are created, and work with a large project (over 1000 lines of code). For this, I recreated Plunder; a card/board game where you play against another player as a pirate competing for gold, as a video game.

Important Note: Game assets (such as images) have been removed from this GitHub repository. In order for the code to work you would need to add these images back in.

Technical Overview: Plunder uses Pygame as a base for building the game, and a custom built server/network to connect clients. Here's how it works:
  1. Uses the class Game to hold information that is important for both players to know.
  2. Each players important information is sent from individual clients to the server using strings and the network class.
  3. The server runs different functions depending on the incoming string, that update the Game class.
  4. The server sends the Game object to each client using Pickle and the network class.
  5. Individual clients update client side information using the Game class object from the server.

Current State of the Project: Abandoned. 
  - I learned what I wanted to from the project and so decided to move on to other projects.
  - In the current state, Plunder has most of the base mechanics of the game implemented.
