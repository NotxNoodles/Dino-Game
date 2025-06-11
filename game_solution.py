import tkinter as tk
from tkinter import PhotoImage
import random
import webbrowser
import json
import os
SAVE_FILE = "game_save.json"

class DinoGame:
    def __init__(self, root):
        '''
        Initialize the Dino Game application.

        This method sets up the main game window, initializes game settings, 
        loads saved states if available, and displays the main menu.
        '''
        self.root = root
        self.root.title("Dino Game")
        self.leaderboard = [] #the leaderboard is a tuple
        self.paused = False
        self.keybinds = {"jump": "space", "pause": "p", "boss_key": "b"}
        self.game_running = False
        self.saved_state = False
        self.invincible = False  
        self.background_image = PhotoImage(file="background.png")
        self.load_initial_state()
        self.main_menu()
        self.apply_keybinds()  

    def main_menu(self):
        """
        Sets up and displays the main menu of the game.

        The main menu allows the player to:
        - Enter their name.
        - Start a new game.
        - Load a saved game, if available.
        - Access the settings menu.
        - View the leaderboard with top player scores.

        The menu frame includes:
        - A title at the top.
        - An input for the player's name.
        - Buttons for "Start Game", "Load Game", and "Settings".
        - A leaderboard displaying the top scores.

        The function also ensures:
        - Background image is set.
        - Keybindings (e.g., boss key) are unbound temporarily to avoid interference.
        - The "Load Game" button is disabled if no save file is available.
        """
        #Gets rid of widgets on the screen so it doesnt open on a new window
        for widget in self.root.winfo_children():
            widget.destroy()

        self.apply_keybinds()  # Ensure keybindings are up-to-date

        # Unbind the boss key to prevent interference with text input
        self.root.unbind(f"<{self.keybinds['boss_key']}>")

            # Create a canvas for the main menu
        self.menu_canvas = tk.Canvas(self.root, width=800, height=400)
        self.menu_canvas.pack(fill="both", expand=True)

        # Add the background image to the canvas
        self.menu_canvas.create_image(0, 0, image=self.background_image, anchor="nw")
        
        # Create a frame over the canvas for widgets
        self.menu_frame = tk.Frame(self.menu_canvas, bg="beige", width=800, height=400)
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Settings button in the top-left corner
        settings_button = tk.Button(
            self.menu_frame, text="Settings", font=("Arial", 14, "bold"), command=self.settings_menu
        )
        settings_button.place(x=10, y=10)  # Positioned in the top-left corner

        # Adding the game title in the center
        title = tk.Label(self.menu_frame, text="Dino Game", font=("Arial", 30, "bold"), bg="beige", fg="black")
        title.pack(pady=(30, 10))  # Padding to position it under the settings button

        # Adding a label prompting the user to enter their name
        name_label = tk.Label(self.menu_frame, text="Enter your name:", font=("Arial", 16, "bold"), bg="beige", fg="black")
        name_label.pack(pady=(10, 5))  # Padding to separate it from the title

        # Adding an entry widget for the player to input their name
        self.name_entry = tk.Entry(self.menu_frame, font=("Arial", 16, "bold"), bg="white", fg="black", bd=2, highlightbackground="black", highlightthickness=2)
        self.name_entry.pack(pady=(0, 10))  # Padding below the entry box

        # Adding the Start Game and Load Game buttons in the same row
        button_frame = tk.Frame(self.menu_frame, bg="beige")
        button_frame.pack(pady=10)

        start_button = tk.Button(
            button_frame, text="Start Game", font=("Arial", 20, "bold"), command=self.save_name_and_start
        )
        start_button.grid(row=0, column=0, padx=10)

        load_button = tk.Button(
            button_frame, text="Load Game", font=("Arial", 20, "bold"), command=self.load_game,
            state=tk.NORMAL if os.path.exists(SAVE_FILE) else tk.DISABLED  # Disable if save file doesn't exist
        )
        load_button.grid(row=0, column=1, padx=10)

        # Leaderboard section
        leaderboard_label = tk.Label(self.menu_frame, text="Leaderboard", font=("Arial", 18, "bold"), bg="beige", fg="black")
        leaderboard_label.pack(pady=(20, 5))  # Padding to separate it from the buttons

        # Display leaderboard entries|f is for formatting
        leaderboard_text = "\n".join([f"{i + 1}. {name}: {score}" for i, (name, score) in enumerate(self.leaderboard)]) #.join takes a list and combines then into a single string
        if not leaderboard_text:  # If no leaderboard entries exist
            leaderboard_text = "No scores yet!"

        leaderboard_display = tk.Label(self.menu_frame, text=leaderboard_text, font=("Arial", 14, "bold"), bg="beige", fg="black", justify="left")
        leaderboard_display.pack()
                
    def save_name_and_start(self):
        """
        Save the player's name and start the game.

        This method retrieves the player's name from the name entry field
        in the main menu. If no name is provided, it defaults to "Player."
        The name is stored in the `self.player_name` attribute, and the 
        game is started by calling the `start_game` method.

        Functionality:
        - Reads the player's input from the name entry field.
        - Assigns a default name ("Player") if no input is provided.
        - Starts the game by transitioning to the gameplay screen.
        """

        # Save the player's name and start the game
        self.player_name = self.name_entry.get() if self.name_entry.get() else "Player" # Save the player's name or default to "Player"
        self.start_game() # Calling the method to start the game

    def start_game(self):
        """
        Transition from the main menu to the gameplay screen.

        This method clears all widgets from the main menu or any current 
        screen and initializes the game setup by calling the `setup_game` method.

        Functionality:
        - Removes all widgets currently displayed on the screen.
        - Initiates the game by setting up the gameplay environment.
        """
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_game()

    def setup_game(self, load_state = False):
        """
        Set up the gameplay environment and initialize game elements.

        This method creates the game canvas, initializes the dino character, obstacles, 
        score display, and other game components. It also binds key controls and optionally 
        loads a saved game state.

        Args:
            load_state (bool): If True, the method loads the saved game state 
                            (e.g., score, obstacles, dino position). Defaults to False.

        Functionality:
        - Creates a canvas for the game environment.
        - Adds the dino character and ground elements to the canvas.
        - Initializes or loads obstacles, key bindings, and the score display.
        - Handles game physics such as gravity and movement speed.
        - Binds controls for jumping, pausing, and the boss key.
        - Supports loading a saved game state for resuming gameplay.
        """
        self.canvas = tk.Canvas(self.root, width=800, height=400, bg="beige") # Creating the game canvas
        self.canvas.pack() # Packing the canvas to make it visible
        #Background Image
        self.canvas.create_image(0, 0, image=self.background_image, anchor="nw")

        #Setting the dino
        self.dino_y = 248 # The initial vertical position of the dino
        self.dino_jump = False
        
        # Add cheat code listener
        self.root.bind("<Key>", self.handle_cheat_code)
        
        #Attributes of starting the game
        self.jump_speed = -15 
        self.gravity = 1.15
        self.obstacles = []
        self.game_running = True
        self.score = 0
        self.paused = False 

        # Adding the dino image to the canvas
        self.dino_image = tk.PhotoImage(file="dino_big.png")
        self.dino = self.canvas.create_image(75, self.dino_y + 25, image=self.dino_image)  

        #Setting the speed
        self.obstacle_speed = 5
        self.speed_increase_interval = 5000 # Speed increases every 5 seconds
        self.max_speed = 25
        self.root.after(self.speed_increase_interval, self.increase_speed)

        #Setting the ground
        self.ground = self.canvas.create_rectangle(0, 350, 800, 400, fill="black")
        self.obstacle_images = [tk.PhotoImage(file="rock_new.png")]

        # Display the score on the canvas
        self.score_text = self.canvas.create_text(
            750, 20, text=f"Score: {self.score}", font=("Arial", 24, "bold"), fill="blue", anchor="e"
        )
        
        # Apply the updated keybinds
        self.apply_keybinds()
        
        if load_state:
            self.load_saved_state()
        else:
            self.create_obstacles()
        
        self.increase_speed() 
        self.update_game() 
        self.increment_score()

    def jump(self, event):
        """
        Handles the jump action for the dinosaur character.

        This method is triggered by a key press event when the associated 
        jump keybind is activated. It initiates the jump action by setting
        the `dino_jump` attribute to `True` and assigning the initial jump 
        speed to the `dino_speed` attribute. The jump will only be initiated
        if the game is not paused and the dinosaur is not already jumping.

        Parameters:
            event (tkinter.Event): The event object containing information 
            about the key press that triggered the jump action.
        """
        if not self.dino_jump and not self.paused:
            self.dino_jump = True
            self.dino_speed = self.jump_speed

    #Changed create_obstacles to make it more playable
    def create_obstacles(self):
        """
        Creates and positions obstacles on the game canvas.

        This method generates obstacles at random positions 
        within a range and adds them to the game canvas. 
        The obstacles are represented as images and stored in the 
        `obstacles` list. The obstacles are spaced apart randomly 
        to make gameplay more dynamic.

        """
        # Ensure no duplicate obstacles are created if some already exist
        if not self.obstacles:
            # Initial horizontal position for the first obstacle
            x_position = random.randint(750, 850)
            for _ in range(2):
                obstacle_image = self.obstacle_images
                obstacle = self.canvas.create_image(x_position, 340, image=obstacle_image) #The 340 is the Y-level at which the obstacle generates
                self.obstacles.append((obstacle, obstacle_image))
                # Increment the horizontal position for the next obstacle, 
                # with a random spacing between 400 and 800 pixels
                x_position += random.randint(400, 800)

    def update_game(self):
        """
        Updates the game state and redraws game elements.

        This method handles the dino's jumping mechanics, moves obstacles,
        checks for collisions, and updates the game canvas. It continuously
        schedules itself to run at a regular interval as long as the game is
        running and not paused.
        """
        
        if not self.game_running or self.paused:
            return

        # Handle the dino's jumping mechanics
        if self.dino_jump:
            self.dino_y += self.dino_speed
            self.dino_speed += self.gravity
            if self.dino_y >= 248: # Check if the dino has landed
                self.dino_y = 248
                self.dino_jump = False
        self.canvas.coords(self.dino, 75, self.dino_y + 26) # Update the dino's position on the canvas

        # Move obstacles and check for collisions
        for obstacle, _ in self.obstacles:
            self.canvas.move(obstacle, -self.obstacle_speed, 0) # Move the obstacles to the left
            if self.canvas.coords(obstacle)[0] < 0: # Check if the  first obstacle has left the screen
                x_position = random.randint(800, 1100) # Generate a new starting position
                self.canvas.coords(obstacle, x_position, 340) # Reset the obstacle's position
            if self.check_collision(obstacle):
                self.game_over()

        self.root.after(30, self.update_game) # Schedule the next update

    def check_collision(self, obstacle):
        """
        Checks if the dinosaur collides with a given obstacle using
        bbox.
        bbox gives the coordinates for the top left and bottom right corners
        x1,y1,x2,y2

        Returns:
            bool: True if a collision is detected, False otherwise.
        """
        if self.invincible:
            return False  # No collision during invincibility
        # Get bounding boxes for the dino and the obstacle
        dino_coords = self.canvas.bbox(self.dino)
        obstacle_coords = self.canvas.bbox(obstacle)
        
        #Collision margins
        dino_vertical_margin = 7
        dino_horizontal_margin = 30
        obstacle_margin =30

        #Changing coords for dino based on margins
        adjusted_dino_coords = (
            dino_coords[0] + dino_horizontal_margin,
            dino_coords[1] + dino_vertical_margin,
            dino_coords[2] - dino_horizontal_margin,
            dino_coords[3] - dino_vertical_margin,
        )
        #Changing coords for obstacle based on margins
        adjusted_obstacle_coords = (
            obstacle_coords[0] + obstacle_margin,
            obstacle_coords[1] + obstacle_margin,
            obstacle_coords[2] - obstacle_margin,
            obstacle_coords[3] - obstacle_margin,
        )
        #Checks if there is actually a collision
        return (
            adjusted_dino_coords[2] > adjusted_obstacle_coords[0]
            and adjusted_dino_coords[0] < adjusted_obstacle_coords[2]
            and adjusted_dino_coords[3] > adjusted_obstacle_coords[1]
            and adjusted_dino_coords[1] < adjusted_obstacle_coords[3]
        )
    #Increasing Score
    def increment_score(self):
        """
        Increments score my 1 every 100ms and displays it
        in the top right
        """
        if self.game_running and not self.paused:
            self.score += 1
            self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")
            self.root.after(100, self.increment_score) #Increasing every 100ns

    def increase_speed(self):
        """
        Increases speed by 0.75 if the game is not paused and if speed is below the max_speed.
        Continues to increase speed every speed_increase_interval
        """
        if self.obstacle_speed < self.max_speed and not self.paused:
            self.obstacle_speed += 0.75
        self.root.after(self.speed_increase_interval, self.increase_speed)

    def game_over(self):
        """
        Ends the current game, displays the "Game Over" screen, updates the leaderboard, 
        and provides options to restart the game.
        """
        #Stop the game
        self.game_running = False

        # Clear the saved game state after death
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)
            self.saved_state = False  # Ensure the main menu reflects the cleared state
        
        # Save player score to leaderboard
        self.leaderboard.append((self.player_name, self.score))
        self.leaderboard = sorted(self.leaderboard, key=lambda x: x[1], reverse=True)[:5]  # Top 5

        # Display "Game Over"
        self.canvas.create_text(400, 100, text="Game Over", font=("Arial", 30, "bold"), fill="red")

        # Display Leaderboard
        leaderboard_text = "Leaderboard:\n"
        for i, (name, score) in enumerate(self.leaderboard, 1):
            leaderboard_text += f"{i}. {name}: {score}\n"
        self.canvas.create_text(400, 212, text=leaderboard_text, font=("Arial", 20, "bold"), fill="#00008B")

        # Restart Button
        restart_button = tk.Button(
            self.root, text="Restart Game", font=("Arial", 14, "bold"), command=self.restart_game
        )
        restart_button.pack()
        
    def pause(self, event = None):
        """
        Toggles the game's paused state. If the game is paused, it displays the 
        pause menu. If the game is resumed, it clears the pause menu and continues gameplay.

        event (tkinter.Event, optional): Triggered when a key is pressed to pause/unpause.
        """
        if not self.game_running:
            return
        
        self.paused = not self.paused #Pause the game
        
        if self.paused:
            self.canvas.create_text(400, 200, text="Paused", font=("Arial", 30, "bold"), fill="red", tag="pause_text")
            self.show_pause_menu()
        else:
            self.canvas.delete("pause_text")  # Remove the "Paused" text
            # Destroy the pause menu frame if it exists
            # the hasattr ensures the program doesn't crash if pause_menu_frame hasn't been created yet.
            if hasattr(self, "pause_menu_frame"):
                self.pause_menu_frame.destroy()
            # Resume the game by restarting the game loop
            self.update_game()
            self.increment_score()

    
    def boss_key(self, event = None):
        """
        When the game is running and the key is pressed, it takes you to google.com.
        If the game is not paused, it will pause the game for you
        """
        if not self.game_running:
            return
        if not self.paused:  # Only pause if the game is not already paused
            self.paused = True  # Set the game to paused state
            self.canvas.create_text(400, 200, text="Paused", font=("Arial", 30,), fill="red", tag="pause_text")  # Show "Paused" text
        webbrowser.open("https://www.google.com")  # Open Google.com

    def restart_game(self):
        """
        Resets the game to its initial state and returns to the main menu.

        This method clears all widgets currently displayed in the game window,
        re-applies the keybindings to ensure they are up-to-date, and returns the user
        to the main menu for a fresh game start.
        """
        for widget in self.root.winfo_children():
            widget.destroy()
        self.apply_keybinds()  # Ensure keybindings are reapplied
        self.main_menu()
    
    def load_initial_state(self):
        """
        Loads the initial game state from a save file if it exists.

        This method attempts to load the game state, including the leaderboard
        and keybindings, from a pre-defined save file. If the file does not exist 
        or the content is invalid, it initializes the game with default settings.
        """
        try:
            with open(SAVE_FILE, "r") as save_file:
                game_state = json.load(save_file)
                # Check if the saved state is valid
                if "score" in game_state and "keybinds" in game_state:
                    self.leaderboard = game_state.get("leaderboard", [])
                    self.keybinds = game_state.get("keybinds", self.keybinds)
                    self.saved_state = True
                else:
                    self.saved_state = False
        except (FileNotFoundError, json.JSONDecodeError):
            # If the save file is missing or cannot be read, initialize defaults
            self.leaderboard = []
            self.keybinds = {"jump": "space", "pause": "p", "boss_key": "b"}
            self.saved_state = False
    
    def save_game_state(self):
        """
        Saves the current game state to a predefined save file.

        This method collects important game data, such as the player's name, score,
        dino's position, obstacles, keybindings, and leaderboard, and writes it to a 
        JSON file. It ensures that the game can be resumed later with the same state.

        """
        game_state = {
            "player_name": getattr(self, "player_name", "Player"),
            "score": getattr(self, "score", 0),
            "dino_y": getattr(self, "dino_y", 300),
            "dino_jump": getattr(self, "dino_jump", False),
            "dino_speed": getattr(self, "dino_speed", 0),
            "obstacle_speed": getattr(self, "obstacle_speed", 5),
            "keybinds": self.keybinds,
            "leaderboard": self.leaderboard,
        }
        
        # Save obstacle positions and their respective image indexes
        if hasattr(self, "canvas") and self.canvas:
            try:
                game_state["obstacles"] = []
                for obstacle in getattr(self, "obstacles", []):
                    coords = self.canvas.coords(obstacle[0])  # Get obstacle position
                    if coords:  # Ensure the obstacle still exists
                        image_index = (
                            self.obstacle_images.index(obstacle[1])
                            if obstacle[1] in self.obstacle_images
                            else 0  # Default to the first image if not found
                        )
                        game_state["obstacles"].append({
                            "x": coords[0],
                            "y": coords[1],
                            "image_index": image_index
                        })
            except tk.TclError:
                game_state["obstacles"] = []  # Handle invalid obstacles gracefully
        else:
            game_state["obstacles"] = []  # No obstacles to save if the canvas is not available
    
        # Write the game state to the save file
        try:
            with open(SAVE_FILE, "w") as save_file:
                json.dump(game_state, save_file)
        except IOError as e:
            print(f"Error saving game state: {e}")

    def save_name_and_start(self):
        """
        Saves the player's entered name and starts the game.

        retrieves the player's name from the name entry widget on the main menu.
        If no name is entered, it defaults to Player. It then transitions the game to 
        the main gameplay by calling the `start_game` method.
        """
        self.player_name = self.name_entry.get() if self.name_entry.get() else "Player"
        self.start_game()

    def start_game(self):
        """
        Starts a new game by transitioning from the current screen to the gameplay setup.

        clears all widgets from the current window to prepare the game environment.
        Calls the `setup_game` method to initialize the gameplay canvas, obstacles, 
        and other game elements.
        """
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_game()
        
    def load_saved_state(self):
        """
        Loads a previously saved game state from the save file and restores gameplay elements.

        Retrieves game data from a JSON file (`SAVE_FILE`) and restores the player's 
        progress, such as the player's name, score, keybindings, dino position, and obstacles. 
        If obstacles are not present in the save file, it regenerates them to ensure proper gameplay.
        """
        try:
            with open(SAVE_FILE, "r") as save_file:
                game_state = json.load(save_file)

            # Restore player and game state
            self.player_name = game_state.get("player_name", "Player")
            self.score = game_state.get("score", 0)
            self.dino_y = game_state.get("dino_y", 248)
            self.dino_jump = game_state.get("dino_jump", False)
            self.dino_speed = game_state.get("dino_speed", 0)
            self.obstacle_speed = game_state.get("obstacle_speed", 5)
            self.keybinds = game_state.get("keybinds", self.keybinds)  # Load saved keybinds

            self.apply_keybinds()  # Apply the loaded keybindings

            # Clear existing obstacles
            self.obstacles = []

            # Recreate obstacles based on saved positions
            obstacle_data = game_state.get("obstacles", [])
            for obstacle_info in obstacle_data:
                x = obstacle_info.get("x", 800)  # Default to off-screen if missing
                y = obstacle_info.get("y", 340)  # Default ground position
                image_index = obstacle_info.get("image_index", 0)  # Default to the first image
                obstacle_image = self.obstacle_images[image_index]
                obstacle = self.canvas.create_image(x, y, image=obstacle_image)
                self.obstacles.append((obstacle, obstacle_image))


            # Fallback: Create new obstacles if none were loaded
            if not self.obstacles:
                self.create_obstacles()

            # Update score display
            self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")
            
            # Handle invincibility state
            if self.invincible:
                self.canvas.create_text(
                    400, 50, text="Invincibility Activated!\nFor 10 Seconds", font=("Arial", 20, "bold"), fill="green", tag="invincible_text"
                )

            self.paused = True  # Keep the game paused after loading

            # Display the pause menu
            self.show_pause_menu()

        except Exception as e:
            print(f"Error loading saved state: {e}")
                    
    def show_pause_menu(self):
        """
        Displays the pause menu when the game is paused.

        Creates a small frame in the center of the game window with buttons 
        for "Save and Quit" and "Resume". The pause menu is displayed when the game 
        is paused, allowing the player to choose whether to save their progress and return 
        to the main menu or resume the game.
        """
        # Create a frame for the pause menu buttons
        self.pause_menu_frame = tk.Frame(self.root, bg = "", highlightthickness= 0, width=200, height=100)
        self.pause_menu_frame.place(relx=0.5, rely=0.5, anchor="center")  # Center the frame

        # Save and Quit button
        save_and_quit_button = tk.Button(
            self.pause_menu_frame, text="Save and Quit", font=("Arial", 14, "bold"), command=self.save_and_quit
        )
        save_and_quit_button.pack(pady=10)
        
        # Resume button
        resume_button = tk.Button(
            self.pause_menu_frame, text="Resume", font=("Arial", 14, "bold"), command=self.pause
        )
        resume_button.pack(pady=10)
    
    def save_and_quit(self):
        """
        Saves the current game state and navigates to the main menu.
        """
        self.save_game_state()
        self.main_menu()
    
    def load_game(self):
        """
        Loads a previously saved game state and starts the game.

        This method clears the current game window and transitions to the gameplay screen 
        with the saved progress. It ensures that the saved game state is properly restored 
        and the game starts in the same state as it was when saved.

        """
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_game(load_state=True)
        
    def save_keybinds(self):
        """
        Unbinds the old keys and updates the new ones
        """
        # Unbind previous keybinds
        for action, old_key in self.keybinds.items():
            self.root.unbind(f"<{old_key}>")
            
        # Validate and update keybinds
        new_keybinds = {
            "jump": self.jump_entry.get().strip().lower() or "space",
            "pause": self.pause_entry.get().strip().lower() or "p",
            "boss_key": self.boss_entry.get().strip().lower() or "b",
        }

        # Update the keybinds dictionary
        self.keybinds.update(new_keybinds)

        # Rebind new keybinds
        self.apply_keybinds()

        # Save the updated keybinds to the game state
        self.save_game_state()

        # Return to the main menu
        self.main_menu()
    
    def apply_keybinds(self):
        """
        Apply the current keybindings.
        """
        # Rebind all actions to their new keys
        self.root.bind(f"<{self.keybinds['jump']}>", self.jump)
        self.root.bind(f"<{self.keybinds['pause']}>", self.pause)
        self.root.bind(f"<{self.keybinds['boss_key']}>", self.boss_key)
            
    def settings_menu(self):
        """
        Displays the settings menu, allowing the player to change keybinds.
        """
 
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create a frame for the settings menu
        self.settings_frame = tk.Frame(self.root, bg="beige", width=800, height=400)
        self.settings_frame.pack_propagate(False)
        self.settings_frame.pack(fill="both", expand=True)

        title = tk.Label(self.settings_frame, text="Settings", font=("Arial", 30, "bold"), bg="beige", fg="black")
        title.pack(pady=20)

        # Jump keybind setting
        jump_label = tk.Label(self.settings_frame, text="Jump Key:", font=("Arial", 16, "bold"), bg="beige")
        jump_label.pack(pady=5)
        self.jump_entry = tk.Entry(self.settings_frame, font=("Arial", 16, "bold"))
        self.jump_entry.insert(0, self.keybinds["jump"])  # Pre-fill with the current keybind
        self.jump_entry.pack(pady=5)

        # Pause keybind setting
        pause_label = tk.Label(self.settings_frame, text="Pause Key:", font=("Arial", 16, "bold"), bg="beige")
        pause_label.pack(pady=5)
        self.pause_entry = tk.Entry(self.settings_frame, font=("Arial", 16, "bold"))
        self.pause_entry.insert(0, self.keybinds["pause"])
        self.pause_entry.pack(pady=5)

        # Boss keybind setting
        boss_label = tk.Label(self.settings_frame, text="Boss Key:", font=("Arial", 16, "bold"), bg="beige")
        boss_label.pack(pady=5)
        self.boss_entry = tk.Entry(self.settings_frame, font=("Arial", 16, "bold"))
        self.boss_entry.insert(0, self.keybinds["boss_key"])
        self.boss_entry.pack(pady=5)

        # Save and Back buttons
        button_frame = tk.Frame(self.settings_frame, bg="beige")
        button_frame.pack(pady=20)

        save_button = tk.Button(
            button_frame, text="Save", font=("Arial", 16, "bold"), command=self.save_keybinds
        )
        save_button.pack(side=tk.LEFT, padx=10)

        back_button = tk.Button(
            button_frame, text="Back", font=("Arial", 16, "bold"), command=self.main_menu
        )
        back_button.pack(side=tk.LEFT, padx=10)
    
    # Activate invincibility mode with a single key
    def handle_cheat_code(self, event):
        """
        Handles cheat code activation during the game.

        This method listens for specific keypress events during gameplay to 
        trigger cheat codes. Currently, it checks for the "C" key to activate 
        invincibility mode, which prevents collisions with obstacles for a limited 
        duration.
        """
        if event.char.lower() == "c" and self.game_running:
            self.activate_invincibility()
    

    def activate_invincibility(self):
        """
        Activates invincibility mode for the player.
        """
        # Check if invincibility is not already active
        if not self.invincible:
            self.invincible = True
            # Display a message on the game canvas to indicate invincibility
            self.canvas.create_text(
                400, 50, text="Invincibility Activated!\nFor 10 Seconds", font=("Arial", 20, "bold"), fill="green", tag="invincible_text"
            )
            # Disable collision detection
            self.root.after(10000, self.deactivate_invincibility)  # Invincibility lasts for 10 seconds
    

    def deactivate_invincibility(self):
        """
        Deactivates invincibility mode for the player.
        """
        self.invincible = False
        self.canvas.delete("invincible_text")
    

    
if __name__ == "__main__":
    """
    Entry point of the Dino Game application.

    This block initializes the main Tkinter root window, creates an instance 
    of the DinoGame class, and starts the Tkinter main event loop.

    The game is executed when this script is run directly. It sets up the 
    graphical user interface (GUI) and starts listening for user inputs 
    and events.
    """
    root = tk.Tk() # Create the main Tkinter window
    game = DinoGame(root) # Instantiate the DinoGame class
    root.mainloop() # Start the Tkinter main loop