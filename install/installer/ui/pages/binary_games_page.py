"""
Binary games setup page for the Arcade Station Installer
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import uuid
import tomllib
import logging

from .base_page import BasePage
from ...utils.game_id import generate_game_id, validate_game_id, get_display_name

class GameEntry:
    """A class representing a binary game entry in the UI."""
    
    def __init__(self, parent, container, app, on_delete_callback):
        """Initialize a game entry.
        
        Args:
            parent: The parent widget (ScrolledFrame)
            container: The container frame for this entry
            app: The main application instance
            on_delete_callback: Callback function when the delete button is clicked
        """
        self.parent = parent
        self.container = container
        self.app = app
        self.on_delete = on_delete_callback
        self.id = str(uuid.uuid4())[:8]  # Generate a unique ID for this entry
        
        self.frame = ttk.Frame(container)
        self.frame.pack(fill="x", padx=5, pady=5)
        
        # Add a separator line
        separator = ttk.Separator(self.frame, orient="horizontal")
        separator.pack(fill="x", pady=5)
        
        # Game name
        name_frame = ttk.Frame(self.frame)
        name_frame.pack(fill="x", pady=2)
        
        name_label = ttk.Label(
            name_frame,
            text="Game Name:",
            width=15
        )
        name_label.pack(side="left", padx=(0, 5))
        
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(
            name_frame,
            textvariable=self.name_var,
            width=30
        )
        name_entry.pack(side="left", fill="x", expand=True)
        
        # Delete button
        delete_button = ttk.Button(
            name_frame,
            text="Delete",
            command=self.delete,
            width=10
        )
        delete_button.pack(side="right", padx=5)
        
        # Unique ID
        id_frame = ttk.Frame(self.frame)
        id_frame.pack(fill="x", pady=2)
        
        id_label = ttk.Label(
            id_frame,
            text="Unique ID:",
            width=15
        )
        id_label.pack(side="left", padx=(0, 5))
        
        self.id_var = tk.StringVar(value=self.id)
        self.id_entry = ttk.Entry(
            id_frame,
            textvariable=self.id_var,
            width=30,
            state="readonly"  # Make it read-only
        )
        self.id_entry.pack(side="left", fill="x", expand=True)
        
        # Add trace to name_var to update ID automatically
        self.name_var.trace_add("write", self._update_id)
        
        # Game executable
        exe_frame = ttk.Frame(self.frame)
        exe_frame.pack(fill="x", pady=2)
        
        exe_label = ttk.Label(
            exe_frame,
            text="Executable:",
            width=15
        )
        exe_label.pack(side="left", padx=(0, 5))
        
        self.exe_var = tk.StringVar()
        exe_entry = ttk.Entry(
            exe_frame,
            textvariable=self.exe_var,
            width=40
        )
        exe_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_button = ttk.Button(
            exe_frame,
            text="Browse...",
            command=self.browse_executable,
            width=10
        )
        browse_button.pack(side="right")
        
        # Game banner
        banner_frame = ttk.Frame(self.frame)
        banner_frame.pack(fill="x", pady=2)
        
        banner_label = ttk.Label(
            banner_frame,
            text="Banner Image:",
            width=15
        )
        banner_label.pack(side="left", padx=(0, 5))
        
        self.banner_var = tk.StringVar()
        banner_entry = ttk.Entry(
            banner_frame,
            textvariable=self.banner_var,
            width=40
        )
        banner_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_image_button = ttk.Button(
            banner_frame,
            text="Browse...",
            command=self.browse_banner,
            width=10
        )
        browse_image_button.pack(side="right")
    
    def _update_id(self, *args):
        """Update the ID when the name changes."""
        name = self.name_var.get().strip()
        if name:
            # Get all existing game IDs from other entries
            existing_ids = {}
            for entry in self.parent.game_entries:
                if entry != self:
                    existing_ids[entry.id_var.get()] = True
            
            # Generate new ID
            new_id = generate_game_id(name, existing_ids)
            self.id_var.set(new_id)
    
    def delete(self):
        """Delete this game entry."""
        self.frame.destroy()
        self.on_delete(self)
    
    def browse_executable(self):
        """Browse for a game executable."""
        filetypes = [
            ("Executable files", "*.exe *.bat *.vbs *.ps1"),
        ] if self.app.install_manager.is_windows else [
            ("All files", "*")
        ]
        
        initial_dir = os.path.dirname(self.exe_var.get()) if self.exe_var.get() else os.path.expanduser("~")
        
        file_path = filedialog.askopenfilename(
            title="Select Game Executable",
            filetypes=filetypes,
            initialdir=initial_dir
        )
        
        if file_path:
            self.exe_var.set(file_path)
            
            # Try to extract a name from the path if none is set
            if not self.name_var.get():
                basename = os.path.basename(file_path)
                name, _ = os.path.splitext(basename)
                self.name_var.set(name)
                
                # Generate a unique ID based on the name
                unique_id = name.lower().replace(" ", "_")
                # Make sure the ID is unique
                self.id_var.set(unique_id)
    
    def browse_banner(self):
        """Browse for a banner image."""
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png")
        ]
        
        # Try to use the assets folder as initial directory
        install_path = self.app.user_config.get("install_path", "")
        assets_path = os.path.join(install_path, "assets", "images", "banners")
        
        # If assets folder exists, use it as initial directory
        if os.path.isdir(assets_path):
            initial_dir = assets_path
        # Otherwise fall back to the current banner path or home directory
        else:
            initial_dir = os.path.dirname(self.banner_var.get()) if self.banner_var.get() else os.path.expanduser("~")
        
        file_path = filedialog.askopenfilename(
            title="Select Banner Image",
            filetypes=filetypes,
            initialdir=initial_dir
        )
        
        if file_path:
            self.banner_var.set(file_path)
    
    def get_data(self):
        """Get the data for this game entry.
        
        Returns:
            dict: Game data
        """
        return {
            "id": self.id_var.get(),
            "display_name": self.name_var.get(),
            "path": self.exe_var.get(),
            "banner": self.banner_var.get()
        }
    
    def validate(self):
        """Validate the game entry.
        
        Returns:
            bool: True if valid, False otherwise
        """
        # Check if name is set
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror(
                "Invalid Name", 
                "Please enter a name for the game."
            )
            return False
        
        # ID validation is automatic now
        game_id = self.id_var.get()
        if not validate_game_id(game_id):
            messagebox.showerror(
                "Invalid ID", 
                f"The game ID '{game_id}' is invalid. Only lowercase letters, numbers, and underscores are allowed."
            )
            return False
        
        # Check if executable path is set and exists
        exe_path = self.exe_var.get().strip()
        if not exe_path:
            messagebox.showerror(
                "Invalid Executable", 
                "Please enter the path to the game executable."
            )
            return False
        
        if not os.path.isfile(exe_path):
            messagebox.showerror(
                "Invalid Executable", 
                "The specified executable file does not exist."
            )
            return False
        
        # Check if banner is set and exists (if provided)
        banner_path = self.banner_var.get().strip()
        if banner_path and not os.path.isfile(banner_path):
            messagebox.showerror(
                "Invalid Banner", 
                "The specified banner image file does not exist."
            )
            return False
        
        return True


class BinaryGamesPage(BasePage):
    """Page for configuring binary (executable) games."""
    
    def __init__(self, container, app):
        """Initialize the binary games page."""
        # Initialize game_entries before calling super().__init__
        # because the base class will call create_widgets()
        self.game_entries = []
        
        super().__init__(container, app)
        self.set_title(
            "Binary Games Setup",
            "Configure executable-based games"
        )
    
    def on_enter(self):
        """Called when the page is shown."""
        # Load existing binary games if in reconfigure mode
        if hasattr(self.app, 'is_reconfigure_mode') and self.app.is_reconfigure_mode:
            installed_games_path = os.path.join(self.app.user_config.get("install_path", ""), "config", "installed_games.toml")
            if os.path.exists(installed_games_path):
                try:
                    with open(installed_games_path, "rb") as f:
                        installed_games = tomllib.load(f)
                        if "games" in installed_games:
                            # Clear existing entries
                            for entry in self.game_entries[:]:
                                self.remove_game(entry)
                            
                            # Add entries for each binary game (excluding ITGMania)
                            for game_id, game_info in installed_games["games"].items():
                                if game_id == "itgmania":
                                    continue
                                    
                                if "path" in game_info:  # This is a binary game
                                    entry = GameEntry(self, self.games_frame, self.app, self.remove_game)
                                    entry.id_var.set(game_id)
                                    entry.name_var.set(game_info.get("display_name", game_id))
                                    entry.exe_var.set(game_info.get("path", ""))
                                    entry.banner_var.set(game_info.get("banner", ""))
                                    self.game_entries.append(entry)
                except Exception as e:
                    logging.warning(f"Failed to load existing binary games: {e}")
    
    def create_widgets(self):
        """Create page-specific widgets."""
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Introduction
        intro_text = ttk.Label(
            main_frame,
            text="Add games that are launched directly from executable files. "
                 "These can include OpenITG, NotITG, DDR Grand Prix, or any other "
                 "standalone game. "
                 "Click 'Add Another Game' below to add games, or select Next to skip this page.",
            wraplength=500,
            justify="left"
        )
        intro_text.pack(anchor="w", pady=(0, 20))
        
        # Game Entries frame
        self.entries_frame = ttk.LabelFrame(
            main_frame,
            text="Game Entries",
            padding=(10, 5)
        )
        self.entries_frame.pack(fill="both", expand=True, pady=10)
        
        # Create a container for the scrollable area
        scroll_container = ttk.Frame(self.entries_frame)
        scroll_container.pack(fill="both", expand=True, padx=10)
        
        # Create canvas and scrollbar
        self.entries_canvas = tk.Canvas(scroll_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=self.entries_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.entries_canvas)
        
        # Configure scroll region
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.entries_canvas.configure(
                scrollregion=self.entries_canvas.bbox("all")
            )
        )
        
        # Create window in canvas with fixed width
        self.entries_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Configure canvas
        self.entries_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        self.entries_canvas.pack(side="left", fill="both", expand=True, padx=(5, 0))
        scrollbar.pack(side="right", fill="y", padx=(0, 5))
        
        # Configure canvas to expand with window
        main_frame.bind(
            "<Configure>",
            lambda e: self.entries_canvas.configure(width=e.width - 80)  # Adjusted width calculation
        )
        
        # Add games frame (container for game entries)
        self.games_frame = ttk.Frame(self.scrollable_frame)
        self.games_frame.pack(fill="both", expand=True)
        
        # Create a fixed-height container for the add button
        button_container = ttk.Frame(main_frame, height=60)
        button_container.pack(fill="x", side="bottom", pady=10)
        button_container.pack_propagate(False)  # Prevent container from shrinking
        
        # Add button with larger size and better styling
        add_button = ttk.Button(
            button_container,
            text="Add Another Game",
            command=self.add_game,
            style="Accent.TButton"
        )
        add_button.pack(expand=True, pady=5)
    
    def add_game(self):
        """Add a new game entry."""
        entry = GameEntry(self, self.games_frame, self.app, self.remove_game)
        self.game_entries.append(entry)
        
        # Update the canvas scroll region
        self.scrollable_frame.update_idletasks()
        self.entries_canvas.configure(scrollregion=self.entries_canvas.bbox("all"))
    
    def remove_game(self, entry):
        """Remove a game entry.
        
        Args:
            entry: The GameEntry to remove
        """
        if entry in self.game_entries:
            self.game_entries.remove(entry)
        
        # Update the canvas scroll region
        self.scrollable_frame.update_idletasks()
        self.entries_canvas.configure(scrollregion=self.entries_canvas.bbox("all"))
    
    def validate(self):
        """Validate all game entries."""
        if not self.game_entries:
            # No games added, that's fine
            return True
        
        # Check for duplicate IDs
        ids = [entry.id_var.get() for entry in self.game_entries]
        if len(ids) != len(set(ids)):
            messagebox.showerror(
                "Duplicate IDs", 
                "Each game must have a unique ID. Please fix any duplicates."
            )
            return False
        
        # Validate each entry
        for entry in self.game_entries:
            if not entry.validate():
                return False
        
        return True
    
    def save_data(self):
        """Save the binary games configuration."""
        binary_games = {}
        
        for entry in self.game_entries:
            game_data = entry.get_data()
            if game_data["path"]:  # Only save games with a path
                binary_games[game_data["id"]] = game_data
        
        if binary_games:
            self.app.user_config["binary_games"] = binary_games 