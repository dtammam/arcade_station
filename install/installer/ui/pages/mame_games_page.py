"""
MAME games setup page for the Arcade Station Installer
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import uuid
import tomllib
import logging

from .base_page import BasePage
from ...utils.game_id import generate_game_id, validate_game_id, get_display_name

class MameGameEntry:
    """A class representing a MAME game entry in the UI."""
    
    def __init__(self, parent, container, app, on_delete_callback):
        """Initialize a MAME game entry.
        
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
            textvariable=self.name_var
        )
        name_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Delete button
        delete_button = ttk.Button(
            name_frame,
            text="Delete",
            command=self.delete,
            width=10
        )
        delete_button.pack(side="right")
        
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
            state="readonly"
        )
        self.id_entry.pack(side="left", fill="x", expand=True)
        
        # ROM name
        rom_frame = ttk.Frame(self.frame)
        rom_frame.pack(fill="x", pady=2)
        
        rom_label = ttk.Label(
            rom_frame,
            text="ROM Name:",
            width=15
        )
        rom_label.pack(side="left", padx=(0, 5))
        
        self.rom_var = tk.StringVar()
        rom_entry = ttk.Entry(
            rom_frame,
            textvariable=self.rom_var
        )
        rom_entry.pack(side="left", fill="x", expand=True)
        
        # State (save state)
        state_frame = ttk.Frame(self.frame)
        state_frame.pack(fill="x", pady=2)
        
        state_label = ttk.Label(
            state_frame,
            text="Save State:",
            width=15
        )
        state_label.pack(side="left", padx=(0, 5))
        
        state_container = ttk.Frame(state_frame)
        state_container.pack(side="left", fill="x", expand=True)
        
        self.state_var = tk.StringVar(value="o")
        state_entry = ttk.Entry(
            state_container,
            textvariable=self.state_var,
            width=10
        )
        state_entry.pack(side="left")
        
        # Help for save state
        state_help = ttk.Label(
            state_container,
            text="(Default: 'o' for standard save state)",
            font=("Arial", 9),
            foreground="#555555"
        )
        state_help.pack(side="left", padx=5)
        
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
            textvariable=self.banner_var
        )
        banner_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_image_button = ttk.Button(
            banner_frame,
            text="Browse...",
            command=self.browse_banner,
            width=10
        )
        browse_image_button.pack(side="right")
        
        # Add trace to name_var to update ID automatically
        self.name_var.trace_add("write", self._update_id)
    
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
        """Get the data for this MAME game entry.
        
        Returns:
            dict: Game data
        """
        return {
            "id": self.id_var.get(),
            "display_name": self.name_var.get(),
            "rom": self.rom_var.get(),
            "state": self.state_var.get(),
            "banner": self.banner_var.get()
        }
    
    def validate(self):
        """Validate the game entry."""
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
        
        # Check if ROM name is set
        if not self.rom_var.get().strip():
            messagebox.showerror(
                "Invalid ROM", 
                "Please enter the ROM name for the game."
            )
            return False
        
        # Check if state is set
        if not self.state_var.get().strip():
            messagebox.showerror(
                "Invalid State", 
                "Please enter a save state for the game."
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


class MAMEGamesPage(BasePage):
    """Page for configuring MAME games."""
    
    def __init__(self, container, app):
        """Initialize the MAME games page."""
        # Initialize game_entries before calling super().__init__
        # because the base class will call create_widgets()
        self.game_entries = []
        
        super().__init__(container, app)
        self.set_title(
            "MAME Games Setup",
            "Configure MAME-based arcade games"
        )
    
    def on_enter(self):
        """Called when the page is shown."""
        # Load existing MAME games if in reconfigure mode
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
                            
                            # Add entries for each MAME game
                            for game_id, game_info in installed_games["games"].items():
                                if "rom" in game_info:  # This is a MAME game
                                    entry = MameGameEntry(self, self.games_frame, self.app, self.remove_game)
                                    entry.id_var.set(game_id)
                                    entry.name_var.set(game_info.get("display_name", game_id))
                                    entry.rom_var.set(game_info.get("rom", ""))
                                    entry.state_var.set(game_info.get("state", "o"))
                                    entry.banner_var.set(game_info.get("banner", ""))
                                    self.game_entries.append(entry)
                                    
                                    # Enable MAME if we have games
                                    self.use_mame_var.set(True)
                                    self.toggle_mame_settings()
                except Exception as e:
                    logging.warning(f"Failed to load existing MAME games: {e}")
    
    def create_widgets(self):
        """Create page-specific widgets."""
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Introduction
        intro_text = ttk.Label(
            main_frame,
            text="Add arcade games that run using the MAME emulator. "
                 "You'll need to provide the ROM name and save state for each game."
                 "Select Next with the box unchecked to skip this page.",
            wraplength=500,
            justify="left"
        )
        intro_text.pack(anchor="w", pady=(0, 10))
        
        # MAME configuration frame
        mame_config_frame = ttk.LabelFrame(
            main_frame,
            text="MAME Configuration",
            padding=(10, 5)
        )
        mame_config_frame.pack(fill="x", pady=10)
        
        # Use MAME checkbox
        self.use_mame_var = tk.BooleanVar(value=False)
        use_mame = ttk.Checkbutton(
            mame_config_frame,
            text="I want to use MAME games with Arcade Station",
            variable=self.use_mame_var,
            command=self.toggle_mame_settings
        )
        use_mame.pack(anchor="w", pady=5)
        
        # MAME path
        path_frame = ttk.Frame(mame_config_frame)
        path_frame.pack(fill="x", pady=5)
        
        path_label = ttk.Label(
            path_frame,
            text="MAME Path:",
            width=15
        )
        path_label.pack(side="left", padx=(0, 5))
        
        self.path_var = tk.StringVar()
        path_entry = ttk.Entry(
            path_frame,
            textvariable=self.path_var,
            width=40
        )
        path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_button = ttk.Button(
            path_frame,
            text="Browse...",
            command=self.browse_mame
        )
        browse_button.pack(side="right")
        
        # MAME inipath
        inipath_frame = ttk.Frame(mame_config_frame)
        inipath_frame.pack(fill="x", pady=5)
        
        inipath_label = ttk.Label(
            inipath_frame,
            text="INI Path:",
            width=15
        )
        inipath_label.pack(side="left", padx=(0, 5))
        
        self.inipath_var = tk.StringVar()
        inipath_entry = ttk.Entry(
            inipath_frame,
            textvariable=self.inipath_var,
            width=40
        )
        inipath_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_ini_button = ttk.Button(
            inipath_frame,
            text="Browse...",
            command=self.browse_inipath
        )
        browse_ini_button.pack(side="right")
        
        # Game Entries frame
        self.entries_frame = ttk.LabelFrame(
            main_frame,
            text="Game Entries",
            padding=(10, 5)
        )
        self.entries_frame.pack(fill="both", expand=True, pady=10)
        
        # Create a container for the scrollable area
        scroll_container = ttk.Frame(self.entries_frame)
        scroll_container.pack(fill="both", expand=True, padx=10)  # Added padding
        
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
        self.entries_canvas.pack(side="left", fill="both", expand=True, padx=(5, 0))  # Added padding
        scrollbar.pack(side="right", fill="y", padx=(0, 5))  # Added padding
        
        # Configure canvas to expand with window
        main_frame.bind(
            "<Configure>",
            lambda e: self.entries_canvas.configure(width=e.width - 80)  # Adjusted width calculation
        )
        
        # Add games frame (container for game entries)
        self.games_frame = ttk.Frame(self.scrollable_frame)
        self.games_frame.pack(fill="both", expand=True)
        
        # Create a fixed-height container for the add button
        button_container = ttk.Frame(main_frame, height=60)  # Fixed height container
        button_container.pack(fill="x", side="bottom", pady=10)
        button_container.pack_propagate(False)  # Prevent container from shrinking
        
        # Add button with larger size and better styling
        add_button = ttk.Button(
            button_container,
            text="Add Another MAME-Based Game",
            command=self.add_game,
            style="Accent.TButton"  # Use a more prominent style
        )
        add_button.pack(expand=True, pady=5)
        
        # Set initial state
        self.toggle_mame_settings()
        
        # Don't add a default game entry since MAME is disabled by default
    
    def toggle_mame_settings(self):
        """Show or hide MAME settings based on checkbox state."""
        if self.use_mame_var.get():
            self.entries_frame.pack(fill="both", expand=True, pady=10)
        else:
            self.entries_frame.pack_forget()
    
    def browse_mame(self):
        """Browse for the MAME executable."""
        filetypes = [
            ("Executable files", "*.exe")
        ] if self.app.install_manager.is_windows else [
            ("All files", "*")
        ]
        
        initial_dir = os.path.dirname(self.path_var.get()) if self.path_var.get() else os.path.expanduser("~")
        
        if self.app.install_manager.is_windows:
            file_path = filedialog.askopenfilename(
                title="Select MAME Executable",
                filetypes=filetypes,
                initialdir=initial_dir
            )
        else:
            # For Linux/Mac, let's select the directory
            file_path = filedialog.askdirectory(
                title="Select MAME Directory",
                initialdir=initial_dir
            )
        
        if file_path:
            self.path_var.set(file_path)
            
            # Try to auto-fill the inipath
            mame_dir = os.path.dirname(file_path) if self.app.install_manager.is_windows else file_path
            ini_dir = os.path.join(mame_dir, "ini")
            if os.path.isdir(ini_dir):
                self.inipath_var.set(ini_dir)
    
    def browse_inipath(self):
        """Browse for the MAME inipath directory."""
        initial_dir = self.inipath_var.get() if self.inipath_var.get() else os.path.expanduser("~")
        
        dir_path = filedialog.askdirectory(
            title="Select MAME INI Directory",
            initialdir=initial_dir
        )
        
        if dir_path:
            self.inipath_var.set(dir_path)
    
    def add_game(self):
        """Add a new MAME game entry."""
        entry = MameGameEntry(self, self.games_frame, self.app, self.remove_game)
        self.game_entries.append(entry)
        
        # Update the canvas scroll region
        self.scrollable_frame.update_idletasks()
        self.entries_canvas.configure(scrollregion=self.entries_canvas.bbox("all"))
    
    def remove_game(self, entry):
        """Remove a MAME game entry.
        
        Args:
            entry: The MameGameEntry to remove
        """
        if entry in self.game_entries:
            self.game_entries.remove(entry)
        
        # Update the canvas scroll region
        self.scrollable_frame.update_idletasks()
        self.entries_canvas.configure(scrollregion=self.entries_canvas.bbox("all"))
    
    def validate(self):
        """Validate MAME configuration and game entries."""
        if not self.use_mame_var.get():
            return True
        
        # Validate MAME path
        mame_path = self.path_var.get().strip()
        if not mame_path:
            messagebox.showerror(
                "Invalid MAME Path", 
                "Please enter the path to the MAME executable or directory."
            )
            return False
        
        if not os.path.exists(mame_path):
            messagebox.showerror(
                "Invalid MAME Path", 
                "The specified MAME path does not exist."
            )
            return False
        
        # Validate inipath if provided
        inipath = self.inipath_var.get().strip()
        if inipath and not os.path.exists(inipath):
            messagebox.showerror(
                "Invalid INI Path", 
                "The specified MAME INI path does not exist."
            )
            return False
        
        # If no games, that's fine
        if not self.game_entries:
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
    
    def on_next(self):
        """Override the base class method to prevent config updates when MAME is disabled."""
        if self.validate():
            self.save_data()
            self.on_leave()
            self.app.next_page()
    
    def save_data(self):
        """Save the MAME configuration and game entries."""
        # Clear previous MAME config if it exists
        if "mame_path" in self.app.user_config:
            del self.app.user_config["mame_path"]
        if "mame_inipath" in self.app.user_config:
            del self.app.user_config["mame_inipath"]
        if "mame_games" in self.app.user_config:
            del self.app.user_config["mame_games"]
            
        # Only add MAME configuration if enabled
        if self.use_mame_var.get():
            self.app.user_config["mame_path"] = self.path_var.get().strip()
            
            if self.inipath_var.get().strip():
                self.app.user_config["mame_inipath"] = self.inipath_var.get().strip()
            
            # Save game entries
            mame_games = {}
            for entry in self.game_entries:
                game_data = entry.get_data()
                if game_data["rom"]:  # Only save games with a ROM
                    mame_games[game_data["id"]] = game_data
            
            if mame_games:
                self.app.user_config["mame_games"] = mame_games 