"""
Key bindings configuration page for the Arcade Station Installer
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox

from .base_page import BasePage

class KeyBindingsPage(BasePage):
    """Page for configuring key bindings and process management."""
    
    def __init__(self, container, app):
        """Initialize the key bindings configuration page."""
        # Initialize key_bindings list before super().__init__ which calls create_widgets
        self.key_bindings = []
        super().__init__(container, app)
        self.set_title(
            "Key Bindings Setup",
            "Configure global hotkeys and manage processes"
        )
    
    def create_widgets(self):
        """Create page-specific widgets."""
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Create tabs
        self.key_bindings_tab = ttk.Frame(self.notebook)
        self.process_tab = ttk.Frame(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.key_bindings_tab, text="Key Bindings")
        self.notebook.add(self.process_tab, text="Process Management")
        
        # Set up the key bindings tab
        self._setup_key_bindings_tab()
        
        # Set up the process management tab
        self._setup_process_tab()
    
    def _setup_key_bindings_tab(self):
        """Set up the key bindings tab."""
        # Ensure key_bindings list is initialized
        if not hasattr(self, 'key_bindings'):
            self.key_bindings = []
        
        # Introduction
        intro_text = ttk.Label(
            self.key_bindings_tab,
            text="Configure global hotkeys for Arcade Station. These keys will work from anywhere in the system, including during gameplay."
                 "Examples below that are used by the original author of Arcade Station."
                 "Key syntax is from the Keyboard library - all keys within this link https://github.com/boppreh/keyboard/blob/master/README.md#api",
            wraplength=500,
            justify="left"
        )
        intro_text.pack(anchor="w", pady=(10, 15))
        
        # Keybindings frame
        keybindings_frame = ttk.LabelFrame(
            self.key_bindings_tab,
            text="Key bindings",
            padding=(10, 5)
        )
        keybindings_frame.pack(fill="both", expand=True, pady=10)
        
        # Column headers
        header_frame = ttk.Frame(keybindings_frame)
        header_frame.pack(fill="x", pady=(5, 0))
        
        ttk.Label(
            header_frame,
            text="Function",
            width=50,
            font=("Arial", 9, "bold")
        ).pack(side="left", padx=(5, 5))
        
        ttk.Label(
            header_frame,
            text="Script Path",
            width=40,
            font=("Arial", 9, "bold")
        ).pack(side="left", padx=(5, 5))
        
        ttk.Label(
            header_frame,
            text="Hotkey",
            width=15,
            font=("Arial", 9, "bold")
        ).pack(side="left", padx=(5, 5))
        
        # Separator
        ttk.Separator(keybindings_frame, orient="horizontal").pack(fill="x", padx=5, pady=5)
        
        # Scrollable frame for key bindings
        canvas = tk.Canvas(keybindings_frame)
        scrollbar = ttk.Scrollbar(keybindings_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)
        
        # Default key bindings
        default_bindings = [
            ("Kill all processes and reset pegasus", "../arcade_station/core/common/kill_all_and_reset_pegasus.py", "ctrl+space"),
            ("Take screenshot (Windows)", "../../bin/windows/take_screenshot.vbs", "+"),
            ("Take screenshot (Windows)", "../../bin/windows/take_screenshot.vbs", "/"),
            ("Start streaming", "../arcade_station/core/common/start_streaming.py", "ctrl+f4"),
            ("Restart to kiosk mode (Windows)", "../arcade_station/core/windows/setup_windows_shell.ps1", "ctrl+f3"),
            ("Restart to PC mode (Windows)", "../arcade_station/core/windows/restore_windows_shell.ps1", "ctrl+f2"),
            ("Restart computer (Windows)", "../arcade_station/core/windows/restart_computer.ps1", "ctrl+`"),
            ("Start explorer.exe (Windows)", "C:/Windows/explorer.exe", "ctrl+f6"),
            ("", "", "")  # Empty row for user to add custom binding
        ]
        
        # Add key bindings
        for i, (display_name, script_path, key) in enumerate(default_bindings):
            self._add_key_binding_row(scrollable_frame, i, display_name, script_path, key)
        
        # Add button for adding new key binding
        add_button = ttk.Button(
            keybindings_frame,
            text="Add Key Binding",
            command=lambda: self._add_key_binding_row(
                scrollable_frame, len(self.key_bindings), "", "", ""
            )
        )
        add_button.pack(anchor="w", padx=5, pady=10)
        
        # Key format help
        help_text = ttk.Label(
            keybindings_frame,
            text="Format: 'ctrl+key', 'alt+key', 'shift+key', or just 'key'.",
            font=("Arial", 9),
            foreground="#555555"
        )
        help_text.pack(anchor="w", pady=5, padx=5)
    
    def _add_key_binding_row(self, parent, index, display_name, script_path, key):
        """Add a row for key binding configuration.
        
        Args:
            parent: Parent frame
            index: Row index
            display_name: Display name for the key binding
            script_path: Path to the script
            key: Key combination
        """
        row_frame = ttk.Frame(parent)
        row_frame.pack(fill="x", pady=2)
        
        # Display name field
        display_var = tk.StringVar(value=display_name)
        display_entry = ttk.Entry(
            row_frame,
            textvariable=display_var,
            width=30
        )
        display_entry.pack(side="left", padx=(0, 5))
        
        # Script path field
        script_var = tk.StringVar(value=script_path)
        script_entry = ttk.Entry(
            row_frame,
            textvariable=script_var,
            width=40
        )
        script_entry.pack(side="left", padx=(0, 5))
        
        # Key field
        key_var = tk.StringVar(value=key)
        key_entry = ttk.Entry(
            row_frame,
            textvariable=key_var,
            width=15
        )
        key_entry.pack(side="left", padx=(0, 5))
        
        # Delete button
        delete_button = ttk.Button(
            row_frame,
            text="×",
            width=2,
            command=lambda: self._remove_key_binding_row(row_frame, index)
        )
        delete_button.pack(side="left", padx=(5, 0))
        
        # Save reference to variables
        if index >= len(self.key_bindings):
            self.key_bindings.append((display_var, script_var, key_var, row_frame))
        else:
            self.key_bindings[index] = (display_var, script_var, key_var, row_frame)
    
    def _remove_key_binding_row(self, row_frame, index):
        """Remove a key binding row.
        
        Args:
            row_frame: Frame to remove
            index: Index of the row
        """
        row_frame.destroy()
        if index < len(self.key_bindings):
            self.key_bindings[index] = (None, None, None, None)  # Mark as removed
    
    def _setup_process_tab(self):
        """Set up the process management tab."""
        # Introduction
        intro_text = ttk.Label(
            self.process_tab,
            text="Configure which processes should be automatically terminated when returning to "
                 "the Pegasus frontend.",
            wraplength=500,
            justify="left"
        )
        intro_text.pack(anchor="w", pady=(10, 15))
        
        # Process management frame
        process_frame = ttk.LabelFrame(
            self.process_tab,
            text="Processes to Kill",
            padding=(10, 5)
        )
        process_frame.pack(fill="x", pady=10)
        
        # Text area for process names
        processes_label = ttk.Label(
            process_frame,
            text="Enter process names to kill (one per line):",
            anchor="w"
        )
        processes_label.pack(anchor="w", pady=(5, 0))
        
        # Default process list
        default_processes = """ITGmania.exe
OpenITG.exe
In The Groove.exe
NotITG-v4.2.0.exe
spice.exe
mame.exe
obs64.exe
i_view64.exe
cmd.exe
explorer.exe
gslauncher.exe
i_view64.exe
LightsTest.exe
mame.exe
mame2lit.exe
mame_lights.exe
mmc.exe
notepad.exe
notepad++.exe
outfox.exe
pegasus-fe_windows.exe
regedit.exe
StepMania.exe
Taskmgr.exe
timeout.exe
marquee_image.exe"""
        
        # Create a text widget with scrollbar
        text_frame = ttk.Frame(process_frame)
        text_frame.pack(fill="both", expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.processes_text = tk.Text(
            text_frame,
            height=10,
            width=50,
            yscrollcommand=scrollbar.set
        )
        self.processes_text.pack(side="left", fill="both", expand=True)
        self.processes_text.insert("1.0", default_processes)
        
        scrollbar.config(command=self.processes_text.yview)
        
        # Help text
        help_text = ttk.Label(
            process_frame,
            text="These processes will be terminated when returning to Pegasus or when using the "
                 "kill hotkey.",
            font=("Arial", 9),
            foreground="#555555",
            wraplength=450
        )
        help_text.pack(anchor="w", pady=5)

    def on_enter(self):
        """Override base class method for page-specific actions when entering the page."""
        # Check if there are existing key bindings
        key_bindings = self.app.user_config.get("key_listener", {})
        
        # Set key bindings from existing config if available
        if key_bindings and "key_mappings" in key_bindings:
            # Clear existing bindings
            for _, _, _, row_frame in self.key_bindings:
                if row_frame:
                    row_frame.destroy()
            
            # Clear key bindings list
            self.key_bindings = []
            
            # Add key bindings from config
            scrollable_frame = self.notebook.children["!frame"].winfo_children()[3].winfo_children()[0].winfo_children()[0]
            
            i = 0
            for key, path in key_bindings["key_mappings"].items():
                # Remove quotes if present in the key
                if key.startswith('"') and key.endswith('"'):
                    key = key[1:-1]
                
                # Try to determine a display name based on the path
                display_name = ""
                if "kill_all_and_reset_pegasus" in path:
                    display_name = "Kill all processes and reset pegasus"
                elif "take_screenshot" in path:
                    display_name = "Take screenshot (Windows)"
                elif "start_streaming" in path:
                    display_name = "Start streaming"
                elif "setup_windows_shell" in path:
                    display_name = "Restart to kiosk mode (Windows)"
                elif "restore_windows_shell" in path:
                    display_name = "Restart to PC mode (Windows)"
                elif "restart_computer" in path:
                    display_name = "Restart computer (Windows)"
                elif "explorer.exe" in path:
                    display_name = "Start explorer.exe (Windows)"
                
                self._add_key_binding_row(scrollable_frame, i, display_name, path, key)
                i += 1
            
            # Add an empty row for new bindings
            self._add_key_binding_row(scrollable_frame, i, "", "", "")
        
        # Check if there are existing process settings
        process_config = self.app.user_config.get("processes_to_kill", {})
        process_names = process_config.get("processes", {}).get("names", [])
        
        if process_names:
            # Clear existing text and set from configuration
            self.processes_text.delete("1.0", tk.END)
            self.processes_text.insert("1.0", "\n".join(process_names))

    def validate(self):
        """Validate key bindings configuration."""
        # Check for duplicate key bindings
        used_keys = {}
        for display_var, script_var, key_var, _ in self.key_bindings:
            if not display_var or not key_var or not script_var:
                continue
                
            key = key_var.get().strip()
            if not key:
                continue
                
            if key in used_keys:
                messagebox.showerror(
                    "Duplicate Key Binding",
                    f"The key '{key}' is already used for '{used_keys[key]}'"
                )
                return False
                
            used_keys[key] = display_var.get()
        
        return True
    
    def save_data(self):
        """Save key bindings configuration to the user config."""
        # Save key bindings
        key_mappings = {}
        for _, script_var, key_var, _ in self.key_bindings:
            if not script_var or not key_var:
                continue
                
            key = key_var.get().strip()
            script = script_var.get().strip()
            
            if key and script:
                # Remove quotes if already present to avoid double-quoting
                if key.startswith('"') and key.endswith('"'):
                    key = key[1:-1]
                
                key_mappings[key] = script
        
        key_config = {
            "key_mappings": key_mappings
        }
        self.app.user_config["key_listener"] = key_config
        
        # Save processes to kill
        process_text = self.processes_text.get("1.0", tk.END).strip()
        process_names = [p.strip() for p in process_text.split("\n") if p.strip()]
        
        process_config = {
            "processes": {
                "names": process_names
            }
        }
        self.app.user_config["processes_to_kill"] = process_config 