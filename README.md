# 2D Magic Forest – Ninja Game
A 2D ninja game coded along with this tutorial [ninja-game](https://www.youtube.com/watch?v=2gABYM5M0ww&t=15005s).
<img src="screenshot.png" alt="screenshot" width="600">

Game Entities and Their Roles:
Player: Can move, jump, and shoot magic projectiles. The camera smoothly follows the player to keep them centered on the screen.

Enemies: Move around and can attack the player. Defeating them increases the player’s score.

Projectiles: Used by the player to attack enemies. They are managed with proper collision logic.

Collectibles: Items like coins that the player can pick up. They may provide extra points or health.

Particles (e.g., leaves): Visual effects that make the environment more dynamic and immersive.

This is a 2D side-scrolling platformer game called Magic Forest, developed using Python and the Pygame library as part of my group assignment. I took reference from a YouTube tutorial to understand the basic game structure such as loading maps, setting up a tile-based world, and player movement. However, I used my own logic to build and improve many features to make the game more interesting and complete.  I also added a scoring system that tracks the player’s points, a lives system that gives the player a limited number of retries, and a game over screen that displays the final score and allows restarting. Background music and sound effects are included to make the gameplay enjoyable, and visual features like moving clouds, falling leaves, and screen shake effects add polish. The camera follows the player smoothly to keep the focus in the middle of the screen. If the player dies, they lose a life and either respawn or the game ends when all lives are gone. I also handled level transitions and fixed issues like flickering. This project helped me learn about game loops, event handling, object-oriented programming, and how to bring different parts of a game together. While I used reference material to start, most of the logic, game design, and additional features were built and customized by me.