# Snake Game AI using A* Algorithm

This project is an AI-driven Snake Game built using Python and Pygame.  
The game automatically plays itself using the A* (A-Star) pathfinding algorithm to reach the food while avoiding collisions.

🚀 Features
- Fully automated A* algorithm-based snake movement  
- Dynamic pathfinding with heuristic (Manhattan distance)  
- Collision detection for walls and snake body  
- Adaptive game speed based on score  
- High Score system (saved in a file)  
- Responsive UI with Pygame  
- Clean and modular code  

 🧠 How the A* Algorithm Works
The A* algorithm calculates the shortest and safest path by using:

- `g(n)` → cost from start to current node  
- `h(n)` → heuristic (Manhattan distance to food)  
- `f(n) = g(n) + h(n)`
  
Once the path is found, the snake follows each step to reach the food efficiently.

 🗂 Tech Stack
- Python  
- Pygame  
- A* Search Algorithm  
- Priority Queues (heapq)  

▶️ How to Run the Game
1. Install dependencies:
   pip install pygame
2. Run the file:
   python snake_ai.py

3. A game window will open and the AI snake will start playing automatically.

📬 Author
Pavithra Thupakula  
Snake Game AI using A* Algorithm  


