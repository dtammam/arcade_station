"""
Control configuration page for the Arcade Station Installer
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from .base_page import BasePage

class ControlConfigPage(BasePage):
    """Page for configuring control devices."""
    
    def __init__(self, container, app):
        """Initialize the control configuration page."""
        super().__init__(container, app)
        self.set_title(
            "Controls Setup",
            "Configure input devices and control mapping"
        )
    
    def create_widgets(self):
        """Create page-specific widgets."""
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create notebook for tabs
        control_notebook = ttk.Notebook(main_frame)
        control_notebook.pack(fill="both", expand=True)
        
        # Create tabs
        self.devices_tab = ttk.Frame(control_notebook)
        self.key_bindings_tab = ttk.Frame(control_notebook)
        self.process_tab = ttk.Frame(control_notebook)
        
        # Add tabs to notebook
        control_notebook.add(self.devices_tab, text="Input Devices")
        control_notebook.add(self.key_bindings_tab, text="Key Bindings")
        control_notebook.add(self.process_tab, text="Process Management")
        
        # Set up the devices tab
        self._setup_devices_tab()
        
        # Set up the key bindings tab
        self._setup_key_bindings_tab()
        
        # Set up the process management tab
        self._setup_process_tab()
    
    def _setup_devices_tab(self):
        """Set up the input devices tab."""
        # Introduction
        intro_text = ttk.Label(
            self.devices_tab,
            text="Configure control options for Arcade Station. "
                 "This includes arcade controls, gamepads, and keyboard mapping.",
            wraplength=500,
            justify="left"
        )
        intro_text.pack(anchor="w", pady=(10, 15))
        
        # Controls configuration frame
        controls_frame = ttk.LabelFrame(
            self.devices_tab,
            text="Input Devices",
            padding=(10, 5)
        )
        controls_frame.pack(fill="x", pady=10)
        
        # Device selection
        device_types_frame = ttk.Frame(controls_frame)
        device_types_frame.pack(fill="x", pady=5)
        
        device_label = ttk.Label(
            device_types_frame,
            text="I will use:",
            font=("Arial", 10, "bold"),
        )
        device_label.pack(anchor="w", pady=(0, 5))
        
        # Arcade controls
        self.use_arcade_var = tk.BooleanVar(value=True)
        arcade_check = ttk.Checkbutton(
            device_types_frame,
            text="Arcade Controls (joysticks, buttons)",
            variable=self.use_arcade_var,
            command=self.toggle_arcade_options
        )
        arcade_check.pack(anchor="w", padx=20, pady=2)
        
        # Gamepad controls
        self.use_gamepad_var = tk.BooleanVar(value=True)
        gamepad_check = ttk.Checkbutton(
            device_types_frame,
            text="Gamepads (Xbox, PlayStation, etc.)",
            variable=self.use_gamepad_var,
            command=self.toggle_gamepad_options
        )
        gamepad_check.pack(anchor="w", padx=20, pady=2)
        
        # Keyboard controls
        self.use_keyboard_var = tk.BooleanVar(value=True)
        keyboard_check = ttk.Checkbutton(
            device_types_frame,
            text="Keyboard",
            variable=self.use_keyboard_var,
            command=self.toggle_keyboard_options
        )
        keyboard_check.pack(anchor="w", padx=20, pady=2)
        
        # Arcade controls configuration frame
        self.arcade_frame = ttk.LabelFrame(
            self.devices_tab,
            text="Arcade Controls Configuration",
            padding=(10, 5)
        )
        
        # Number of players
        players_frame = ttk.Frame(self.arcade_frame)
        players_frame.pack(fill="x", pady=5)
        
        players_label = ttk.Label(
            players_frame,
            text="Number of Players:",
            width=20
        )
        players_label.pack(side="left", padx=(0, 5))
        
        self.players_var = tk.IntVar(value=2)
        players_spinbox = ttk.Spinbox(
            players_frame,
            from_=1,
            to=4,
            textvariable=self.players_var,
            width=5
        )
        players_spinbox.pack(side="left")
        
        # Buttons per player
        buttons_frame = ttk.Frame(self.arcade_frame)
        buttons_frame.pack(fill="x", pady=5)
        
        buttons_label = ttk.Label(
            buttons_frame,
            text="Buttons per Player:",
            width=20
        )
        buttons_label.pack(side="left", padx=(0, 5))
        
        self.buttons_var = tk.IntVar(value=8)
        buttons_spinbox = ttk.Spinbox(
            buttons_frame,
            from_=1,
            to=12,
            textvariable=self.buttons_var,
            width=5
        )
        buttons_spinbox.pack(side="left")
        
        # Control interface
        interface_frame = ttk.Frame(self.arcade_frame)
        interface_frame.pack(fill="x", pady=5)
        
        interface_label = ttk.Label(
            interface_frame,
            text="Control Interface:",
            width=20
        )
        interface_label.pack(side="left", padx=(0, 5))
        
        self.interface_var = tk.StringVar(value="xinput")
        interface_combo = ttk.Combobox(
            interface_frame,
            textvariable=self.interface_var,
            values=["xinput", "dinput", "keyboard", "joystick", "custom"],
            width=15
        )
        interface_combo.pack(side="left")
        interface_combo.state(["readonly"])
        
        # Show advanced config option
        advanced_frame = ttk.Frame(self.arcade_frame)
        advanced_frame.pack(fill="x", pady=5)
        
        self.advanced_var = tk.BooleanVar(value=False)
        advanced_check = ttk.Checkbutton(
            advanced_frame,
            text="I want to use an advanced control mapping configuration",
            variable=self.advanced_var,
            command=self.toggle_advanced_options
        )
        advanced_check.pack(anchor="w", padx=5, pady=5)
        
        # Advanced configuration frame
        self.advanced_frame = ttk.Frame(self.arcade_frame)
        
        # Custom mapping file
        mapping_frame = ttk.Frame(self.advanced_frame)
        mapping_frame.pack(fill="x", pady=5)
        
        mapping_label = ttk.Label(
            mapping_frame,
            text="Custom Mapping File:",
            width=20
        )
        mapping_label.pack(side="left", padx=(0, 5))
        
        self.mapping_var = tk.StringVar()
        mapping_entry = ttk.Entry(
            mapping_frame,
            textvariable=self.mapping_var,
            width=40
        )
        mapping_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_mapping_button = ttk.Button(
            mapping_frame,
            text="Browse...",
            command=self.browse_mapping
        )
        browse_mapping_button.pack(side="right")
        
        # Help text
        mapping_help = ttk.Label(
            self.advanced_frame,
            text="Note: Custom mapping files should be in JSON format and "
                 "follow the Arcade Station control mapping schema.",
            font=("Arial", 9),
            foreground="#555555",
            wraplength=500,
            justify="left"
        )
        mapping_help.pack(anchor="w", pady=5)
        
        # Gamepad configuration frame
        self.gamepad_frame = ttk.LabelFrame(
            self.devices_tab,
            text="Gamepad Configuration",
            padding=(10, 5)
        )
        
        # Maximum gamepads
        max_pads_frame = ttk.Frame(self.gamepad_frame)
        max_pads_frame.pack(fill="x", pady=5)
        
        max_pads_label = ttk.Label(
            max_pads_frame,
            text="Maximum Gamepads:",
            width=20
        )
        max_pads_label.pack(side="left", padx=(0, 5))
        
        self.max_pads_var = tk.IntVar(value=4)
        max_pads_spinbox = ttk.Spinbox(
            max_pads_frame,
            from_=1,
            to=8,
            textvariable=self.max_pads_var,
            width=5
        )
        max_pads_spinbox.pack(side="left")
        
        # Gamepad type
        pad_type_frame = ttk.Frame(self.gamepad_frame)
        pad_type_frame.pack(fill="x", pady=5)
        
        pad_type_label = ttk.Label(
            pad_type_frame,
            text="Preferred Type:",
            width=20
        )
        pad_type_label.pack(side="left", padx=(0, 5))
        
        self.pad_type_var = tk.StringVar(value="xbox")
        pad_type_combo = ttk.Combobox(
            pad_type_frame,
            textvariable=self.pad_type_var,
            values=["xbox", "playstation", "nintendo", "generic"],
            width=15
        )
        pad_type_combo.pack(side="left")
        pad_type_combo.state(["readonly"])
        
        # Keyboard configuration frame
        self.keyboard_frame = ttk.LabelFrame(
            self.devices_tab,
            text="Keyboard Configuration",
            padding=(10, 5)
        )
        
        # Keyboard layout
        layout_frame = ttk.Frame(self.keyboard_frame)
        layout_frame.pack(fill="x", pady=5)
        
        layout_label = ttk.Label(
            layout_frame,
            text="Keyboard Layout:",
            width=20
        )
        layout_label.pack(side="left", padx=(0, 5))
        
        self.layout_var = tk.StringVar(value="us")
        layout_combo = ttk.Combobox(
            layout_frame,
            textvariable=self.layout_var,
            values=["us", "uk", "de", "fr", "es", "jp", "custom"],
            width=15
        )
        layout_combo.pack(side="left")
        layout_combo.state(["readonly"])
        
        # Use standard arcade mappings
        standard_frame = ttk.Frame(self.keyboard_frame)
        standard_frame.pack(fill="x", pady=5)
        
        self.standard_var = tk.BooleanVar(value=True)
        standard_check = ttk.Checkbutton(
            standard_frame,
            text="Use standard arcade keyboard mappings",
            variable=self.standard_var,
            command=self.toggle_standard_mappings
        )
        standard_check.pack(anchor="w", padx=5)
        
        # Custom keyboard mapping file
        self.custom_kb_frame = ttk.Frame(self.keyboard_frame)
        
        kb_mapping_frame = ttk.Frame(self.custom_kb_frame)
        kb_mapping_frame.pack(fill="x", pady=5)
        
        kb_mapping_label = ttk.Label(
            kb_mapping_frame,
            text="Custom Keyboard Map:",
            width=20
        )
        kb_mapping_label.pack(side="left", padx=(0, 5))
        
        self.kb_mapping_var = tk.StringVar()
        kb_mapping_entry = ttk.Entry(
            kb_mapping_frame,
            textvariable=self.kb_mapping_var,
            width=40
        )
        kb_mapping_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_kb_button = ttk.Button(
            kb_mapping_frame,
            text="Browse...",
            command=self.browse_kb_mapping
        )
        browse_kb_button.pack(side="right")
        
        # Initialize UI state
        self.toggle_arcade_options()
        self.toggle_gamepad_options()
        self.toggle_keyboard_options()
        self.toggle_advanced_options()
        self.toggle_standard_mappings()
    
    def _setup_key_bindings_tab(self):
        """Set up the key bindings tab."""
        # Introduction
        intro_text = ttk.Label(
            self.key_bindings_tab,
            text="Configure global hotkeys for Arcade Station. These keys will work from anywhere "
                 "in the system, including during gameplay.",
            wraplength=500,
            justify="left"
        )
        intro_text.pack(anchor="w", pady=(10, 15))
        
        # Keybindings frame
        keybindings_frame = ttk.LabelFrame(
            self.key_bindings_tab,
            text="Global Hotkeys",
            padding=(10, 5)
        )
        keybindings_frame.pack(fill="x", pady=10)
        
        # Reset to Pegasus key binding
        reset_frame = ttk.Frame(keybindings_frame)
        reset_frame.pack(fill="x", pady=5)
        
        reset_label = ttk.Label(
            reset_frame,
            text="Kill all games and reset to Pegasus:",
            width=30,
            anchor="w"
        )
        reset_label.pack(side="left", padx=(0, 5))
        
        self.kill_key_var = tk.StringVar(value="ctrl+q")
        reset_entry = ttk.Entry(
            reset_frame,
            textvariable=self.kill_key_var,
            width=15
        )
        reset_entry.pack(side="left")
        
        # Screenshot key binding
        screenshot_frame = ttk.Frame(keybindings_frame)
        screenshot_frame.pack(fill="x", pady=5)
        
        screenshot_label = ttk.Label(
            screenshot_frame,
            text="Take screenshot:",
            width=30,
            anchor="w"
        )
        screenshot_label.pack(side="left", padx=(0, 5))
        
        self.screenshot_key_var = tk.StringVar(value="ctrl+p")
        screenshot_entry = ttk.Entry(
            screenshot_frame,
            textvariable=self.screenshot_key_var,
            width=15
        )
        screenshot_entry.pack(side="left")
        
        # Streaming key binding
        streaming_frame = ttk.Frame(keybindings_frame)
        streaming_frame.pack(fill="x", pady=5)
        
        streaming_label = ttk.Label(
            streaming_frame,
            text="Start/stop streaming:",
            width=30,
            anchor="w"
        )
        streaming_label.pack(side="left", padx=(0, 5))
        
        self.streaming_key_var = tk.StringVar(value="ctrl+b")
        streaming_entry = ttk.Entry(
            streaming_frame,
            textvariable=self.streaming_key_var,
            width=15
        )
        streaming_entry.pack(side="left")
        
        # Key format help
        help_text = ttk.Label(
            keybindings_frame,
            text="Format: 'ctrl+key', 'alt+key', 'shift+key', or just 'key'.",
            font=("Arial", 9),
            foreground="#555555"
        )
        help_text.pack(anchor="w", pady=5)
    
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
i_view64.exe"""
        
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
        """Called when the page is shown."""
        # Pre-populate fields if in reconfiguration mode
        if hasattr(self.app, 'is_reconfigure_mode') and self.app.is_reconfigure_mode:
            # Load key bindings if available
            if 'key_listener' in self.app.user_config:
                key_config = self.app.user_config['key_listener']
                if 'keys' in key_config:
                    keys = key_config['keys']
                    if 'kill_all_and_reset_pegasus' in keys:
                        self.kill_key_var.set(keys['kill_all_and_reset_pegasus'])
                    if 'take_screenshot' in keys:
                        self.screenshot_key_var.set(keys['take_screenshot'])
                    if 'start_streaming' in keys:
                        self.streaming_key_var.set(keys['start_streaming'])
            
            # Load processes to kill
            if 'processes_to_kill' in self.app.user_config:
                proc_config = self.app.user_config['processes_to_kill']
                if 'process_names' in proc_config:
                    process_names = proc_config['process_names']
                    self.processes_text.delete("1.0", tk.END)
                    self.processes_text.insert("1.0", "\n".join(process_names))

    def toggle_arcade_options(self):
        """Show or hide arcade control options based on checkbox state."""
        if self.use_arcade_var.get():
            self.arcade_frame.pack(fill="x", pady=10)
        else:
            self.arcade_frame.pack_forget()
    
    def toggle_gamepad_options(self):
        """Show or hide gamepad options based on checkbox state."""
        if self.use_gamepad_var.get():
            self.gamepad_frame.pack(fill="x", pady=10)
        else:
            self.gamepad_frame.pack_forget()
    
    def toggle_keyboard_options(self):
        """Show or hide keyboard options based on checkbox state."""
        if self.use_keyboard_var.get():
            self.keyboard_frame.pack(fill="x", pady=10)
        else:
            self.keyboard_frame.pack_forget()
    
    def toggle_advanced_options(self):
        """Show or hide advanced control options based on checkbox state."""
        if self.advanced_var.get():
            self.advanced_frame.pack(fill="x", pady=5)
        else:
            self.advanced_frame.pack_forget()
    
    def toggle_standard_mappings(self):
        """Show or hide custom keyboard mapping options based on checkbox state."""
        if not self.standard_var.get():
            self.custom_kb_frame.pack(fill="x", pady=5)
        else:
            self.custom_kb_frame.pack_forget()
    
    def browse_mapping(self):
        """Browse for a control mapping file."""
        filetypes = [
            ("JSON files", "*.json"),
            ("All files", "*.*")
        ]
        
        initial_dir = os.path.dirname(self.mapping_var.get()) if self.mapping_var.get() else os.path.expanduser("~")
        
        file_path = filedialog.askopenfilename(
            title="Select Control Mapping File",
            filetypes=filetypes,
            initialdir=initial_dir
        )
        
        if file_path:
            self.mapping_var.set(file_path)
    
    def browse_kb_mapping(self):
        """Browse for a keyboard mapping file."""
        filetypes = [
            ("JSON files", "*.json"),
            ("All files", "*.*")
        ]
        
        initial_dir = os.path.dirname(self.kb_mapping_var.get()) if self.kb_mapping_var.get() else os.path.expanduser("~")
        
        file_path = filedialog.askopenfilename(
            title="Select Keyboard Mapping File",
            filetypes=filetypes,
            initialdir=initial_dir
        )
        
        if file_path:
            self.kb_mapping_var.set(file_path)
    
    def validate(self):
        """Validate control configuration."""
        # Validate arcade controls
        if self.use_arcade_var.get() and self.advanced_var.get():
            mapping_path = self.mapping_var.get().strip()
            if mapping_path and not os.path.isfile(mapping_path):
                messagebox.showerror(
                    "Invalid Mapping File", 
                    "The specified control mapping file does not exist."
                )
                return False
        
        # Validate keyboard mapping
        if self.use_keyboard_var.get() and not self.standard_var.get():
            kb_mapping_path = self.kb_mapping_var.get().strip()
            if kb_mapping_path and not os.path.isfile(kb_mapping_path):
                messagebox.showerror(
                    "Invalid Keyboard Mapping File", 
                    "The specified keyboard mapping file does not exist."
                )
                return False
        
        # Ensure at least one input type is selected
        if not (self.use_arcade_var.get() or self.use_gamepad_var.get() or self.use_keyboard_var.get()):
            messagebox.showerror(
                "No Input Selected", 
                "Please select at least one input device type."
            )
            return False
        
        return True
    
    def save_data(self):
        """Save control configuration to the user config."""
        controls_config = {}
        
        # Save general input options
        controls_config["use_arcade_controls"] = self.use_arcade_var.get()
        controls_config["use_gamepad"] = self.use_gamepad_var.get()
        controls_config["use_keyboard"] = self.use_keyboard_var.get()
        
        # Save arcade controls configuration
        if self.use_arcade_var.get():
            arcade_config = {
                "players": self.players_var.get(),
                "buttons_per_player": self.buttons_var.get(),
                "interface": self.interface_var.get()
            }
            
            if self.advanced_var.get() and self.mapping_var.get().strip():
                arcade_config["custom_mapping_file"] = self.mapping_var.get().strip()
            
            controls_config["arcade"] = arcade_config
        
        # Save gamepad configuration
        if self.use_gamepad_var.get():
            gamepad_config = {
                "max_gamepads": self.max_pads_var.get(),
                "preferred_type": self.pad_type_var.get()
            }
            
            controls_config["gamepad"] = gamepad_config
        
        # Save keyboard configuration
        if self.use_keyboard_var.get():
            keyboard_config = {
                "layout": self.layout_var.get(),
                "use_standard_mappings": self.standard_var.get()
            }
            
            if not self.standard_var.get() and self.kb_mapping_var.get().strip():
                keyboard_config["custom_mapping_file"] = self.kb_mapping_var.get().strip()
            
            controls_config["keyboard"] = keyboard_config
        
        # Save to user config
        self.app.user_config["controls"] = controls_config
        
        # Save key bindings
        key_config = {
            "keys": {
                "kill_all_and_reset_pegasus": self.kill_key_var.get().strip(),
                "take_screenshot": self.screenshot_key_var.get().strip(),
                "start_streaming": self.streaming_key_var.get().strip()
            }
        }
        self.app.user_config["key_listener"] = key_config
        
        # Save processes to kill
        process_text = self.processes_text.get("1.0", tk.END).strip()
        process_names = [p.strip() for p in process_text.split("\n") if p.strip()]
        
        process_config = {
            "process_names": process_names
        }
        self.app.user_config["processes_to_kill"] = process_config 