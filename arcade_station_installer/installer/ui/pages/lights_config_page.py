"""
Lights configuration page for the Arcade Station Installer
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser

from .base_page import BasePage

class LightsConfigPage(BasePage):
    """Page for configuring cabinet lighting."""
    
    def __init__(self, container, app):
        """Initialize the lights configuration page."""
        super().__init__(container, app)
        self.set_title(
            "Lighting Setup",
            "Configure cabinet lighting and LED options"
        )
    
    def create_widgets(self):
        """Create page-specific widgets."""
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Introduction
        intro_text = ttk.Label(
            main_frame,
            text="Configure lighting options for your cabinet. This includes cabinet LEDs, "
                 "button lighting, and special effects.",
            wraplength=500,
            justify="left"
        )
        intro_text.pack(anchor="w", pady=(0, 15))
        
        # Use lights checkbox
        self.use_lights_var = tk.BooleanVar(value=False)
        use_lights = ttk.Checkbutton(
            main_frame,
            text="I want to use cabinet lighting with Arcade Station",
            variable=self.use_lights_var,
            command=self.toggle_lights_settings
        )
        use_lights.pack(anchor="w", pady=5)
        
        # Lights configuration frame
        self.lights_frame = ttk.LabelFrame(
            main_frame,
            text="Lighting Configuration",
            padding=(10, 5)
        )
        
        # Lighting system type
        system_frame = ttk.Frame(self.lights_frame)
        system_frame.pack(fill="x", pady=5)
        
        system_label = ttk.Label(
            system_frame,
            text="Lighting System:",
            width=20
        )
        system_label.pack(side="left", padx=(0, 5))
        
        self.system_var = tk.StringVar(value="arduino")
        system_combo = ttk.Combobox(
            system_frame,
            textvariable=self.system_var,
            values=["arduino", "pacled64", "ultimarc", "custom"],
            width=15
        )
        system_combo.pack(side="left")
        system_combo.state(["readonly"])
        
        # Arduino settings frame
        self.arduino_frame = ttk.LabelFrame(
            self.lights_frame,
            text="Arduino Settings",
            padding=(10, 5)
        )
        self.arduino_frame.pack(fill="x", pady=5)
        
        # Arduino COM port
        port_frame = ttk.Frame(self.arduino_frame)
        port_frame.pack(fill="x", pady=5)
        
        port_label = ttk.Label(
            port_frame,
            text="COM Port:",
            width=15
        )
        port_label.pack(side="left", padx=(0, 5))
        
        self.port_var = tk.StringVar(value="COM3" if self.app.install_manager.is_windows else "/dev/ttyACM0")
        port_entry = ttk.Entry(
            port_frame,
            textvariable=self.port_var,
            width=15
        )
        port_entry.pack(side="left")
        
        # Arduino sketch
        sketch_frame = ttk.Frame(self.arduino_frame)
        sketch_frame.pack(fill="x", pady=5)
        
        sketch_label = ttk.Label(
            sketch_frame,
            text="Arduino Sketch:",
            width=15
        )
        sketch_label.pack(side="left", padx=(0, 5))
        
        self.sketch_var = tk.StringVar()
        sketch_entry = ttk.Entry(
            sketch_frame,
            textvariable=self.sketch_var,
            width=40
        )
        sketch_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_sketch_button = ttk.Button(
            sketch_frame,
            text="Browse...",
            command=self.browse_sketch
        )
        browse_sketch_button.pack(side="right")
        
        # Number of LEDs
        leds_frame = ttk.Frame(self.arduino_frame)
        leds_frame.pack(fill="x", pady=5)
        
        leds_label = ttk.Label(
            leds_frame,
            text="Number of LEDs:",
            width=15
        )
        leds_label.pack(side="left", padx=(0, 5))
        
        self.leds_var = tk.IntVar(value=60)
        leds_spinbox = ttk.Spinbox(
            leds_frame,
            from_=1,
            to=300,
            textvariable=self.leds_var,
            width=5
        )
        leds_spinbox.pack(side="left")
        
        # Button lighting frame
        self.button_frame = ttk.LabelFrame(
            self.lights_frame,
            text="Button Lighting",
            padding=(10, 5)
        )
        self.button_frame.pack(fill="x", pady=5)
        
        # Use button lighting
        self.use_button_lights_var = tk.BooleanVar(value=True)
        use_button_lights = ttk.Checkbutton(
            self.button_frame,
            text="Enable button lighting",
            variable=self.use_button_lights_var,
            command=self.toggle_button_settings
        )
        use_button_lights.pack(anchor="w", pady=5)
        
        # Button lighting settings frame
        self.button_settings_frame = ttk.Frame(self.button_frame)
        self.button_settings_frame.pack(fill="x", pady=5)
        
        # Player 1 color
        p1_frame = ttk.Frame(self.button_settings_frame)
        p1_frame.pack(fill="x", pady=2)
        
        p1_label = ttk.Label(
            p1_frame,
            text="Player 1 Color:",
            width=15
        )
        p1_label.pack(side="left", padx=(0, 5))
        
        self.p1_color_var = tk.StringVar(value="#FF0000")  # Red
        p1_color_button = ttk.Button(
            p1_frame,
            text="Select Color",
            command=lambda: self.choose_color(self.p1_color_var)
        )
        p1_color_button.pack(side="left")
        
        self.p1_color_preview = tk.Canvas(
            p1_frame,
            width=20,
            height=20,
            bg=self.p1_color_var.get()
        )
        self.p1_color_preview.pack(side="left", padx=5)
        
        # Player 2 color
        p2_frame = ttk.Frame(self.button_settings_frame)
        p2_frame.pack(fill="x", pady=2)
        
        p2_label = ttk.Label(
            p2_frame,
            text="Player 2 Color:",
            width=15
        )
        p2_label.pack(side="left", padx=(0, 5))
        
        self.p2_color_var = tk.StringVar(value="#0000FF")  # Blue
        p2_color_button = ttk.Button(
            p2_frame,
            text="Select Color",
            command=lambda: self.choose_color(self.p2_color_var)
        )
        p2_color_button.pack(side="left")
        
        self.p2_color_preview = tk.Canvas(
            p2_frame,
            width=20,
            height=20,
            bg=self.p2_color_var.get()
        )
        self.p2_color_preview.pack(side="left", padx=5)
        
        # Player 3 color
        p3_frame = ttk.Frame(self.button_settings_frame)
        p3_frame.pack(fill="x", pady=2)
        
        p3_label = ttk.Label(
            p3_frame,
            text="Player 3 Color:",
            width=15
        )
        p3_label.pack(side="left", padx=(0, 5))
        
        self.p3_color_var = tk.StringVar(value="#00FF00")  # Green
        p3_color_button = ttk.Button(
            p3_frame,
            text="Select Color",
            command=lambda: self.choose_color(self.p3_color_var)
        )
        p3_color_button.pack(side="left")
        
        self.p3_color_preview = tk.Canvas(
            p3_frame,
            width=20,
            height=20,
            bg=self.p3_color_var.get()
        )
        self.p3_color_preview.pack(side="left", padx=5)
        
        # Player 4 color
        p4_frame = ttk.Frame(self.button_settings_frame)
        p4_frame.pack(fill="x", pady=2)
        
        p4_label = ttk.Label(
            p4_frame,
            text="Player 4 Color:",
            width=15
        )
        p4_label.pack(side="left", padx=(0, 5))
        
        self.p4_color_var = tk.StringVar(value="#FFFF00")  # Yellow
        p4_color_button = ttk.Button(
            p4_frame,
            text="Select Color",
            command=lambda: self.choose_color(self.p4_color_var)
        )
        p4_color_button.pack(side="left")
        
        self.p4_color_preview = tk.Canvas(
            p4_frame,
            width=20,
            height=20,
            bg=self.p4_color_var.get()
        )
        self.p4_color_preview.pack(side="left", padx=5)
        
        # General lighting frame
        self.general_frame = ttk.LabelFrame(
            self.lights_frame,
            text="General Lighting",
            padding=(10, 5)
        )
        self.general_frame.pack(fill="x", pady=5)
        
        # Default animation
        anim_frame = ttk.Frame(self.general_frame)
        anim_frame.pack(fill="x", pady=5)
        
        anim_label = ttk.Label(
            anim_frame,
            text="Default Animation:",
            width=15
        )
        anim_label.pack(side="left", padx=(0, 5))
        
        self.anim_var = tk.StringVar(value="rainbow")
        anim_combo = ttk.Combobox(
            anim_frame,
            textvariable=self.anim_var,
            values=["off", "static", "rainbow", "breathing", "chase", "reactive"],
            width=15
        )
        anim_combo.pack(side="left")
        anim_combo.state(["readonly"])
        
        # Default brightness
        brightness_frame = ttk.Frame(self.general_frame)
        brightness_frame.pack(fill="x", pady=5)
        
        brightness_label = ttk.Label(
            brightness_frame,
            text="Brightness:",
            width=15
        )
        brightness_label.pack(side="left", padx=(0, 5))
        
        self.brightness_var = tk.IntVar(value=75)
        brightness_scale = ttk.Scale(
            brightness_frame,
            from_=0,
            to=100,
            variable=self.brightness_var,
            orient="horizontal",
            length=200
        )
        brightness_scale.pack(side="left")
        
        brightness_value = ttk.Label(
            brightness_frame,
            textvariable=self.brightness_var,
            width=3
        )
        brightness_value.pack(side="left", padx=5)
        
        percent_label = ttk.Label(
            brightness_frame,
            text="%"
        )
        percent_label.pack(side="left")
        
        # Cabinet layout frame
        self.cabinet_frame = ttk.LabelFrame(
            self.lights_frame,
            text="Cabinet Layout",
            padding=(10, 5)
        )
        self.cabinet_frame.pack(fill="x", pady=5)
        
        # Use marquee
        self.use_marquee_var = tk.BooleanVar(value=True)
        use_marquee = ttk.Checkbutton(
            self.cabinet_frame,
            text="Cabinet has a marquee (top section)",
            variable=self.use_marquee_var
        )
        use_marquee.pack(anchor="w", pady=2)
        
        # Use control panel
        self.use_cp_var = tk.BooleanVar(value=True)
        use_cp = ttk.Checkbutton(
            self.cabinet_frame,
            text="Control panel has RGB underlighting",
            variable=self.use_cp_var
        )
        use_cp.pack(anchor="w", pady=2)
        
        # Use speakers
        self.use_speakers_var = tk.BooleanVar(value=False)
        use_speakers = ttk.Checkbutton(
            self.cabinet_frame,
            text="RGB speaker lighting",
            variable=self.use_speakers_var
        )
        use_speakers.pack(anchor="w", pady=2)
        
        # Advanced settings
        self.advanced_var = tk.BooleanVar(value=False)
        advanced_check = ttk.Checkbutton(
            self.lights_frame,
            text="I want to use advanced lighting configurations",
            variable=self.advanced_var,
            command=self.toggle_advanced_settings
        )
        advanced_check.pack(anchor="w", pady=5)
        
        # Advanced configuration frame
        self.advanced_frame = ttk.Frame(self.lights_frame)
        
        # Custom config file
        config_frame = ttk.Frame(self.advanced_frame)
        config_frame.pack(fill="x", pady=5)
        
        config_label = ttk.Label(
            config_frame,
            text="Custom Config File:",
            width=20
        )
        config_label.pack(side="left", padx=(0, 5))
        
        self.config_var = tk.StringVar()
        config_entry = ttk.Entry(
            config_frame,
            textvariable=self.config_var,
            width=40
        )
        config_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_config_button = ttk.Button(
            config_frame,
            text="Browse...",
            command=self.browse_config
        )
        browse_config_button.pack(side="right")
        
        # Help text
        config_help = ttk.Label(
            self.advanced_frame,
            text="Note: Custom lighting configuration files should be in JSON format and "
                 "follow the Arcade Station lighting configuration schema.",
            font=("Arial", 9),
            foreground="#555555",
            wraplength=500,
            justify="left"
        )
        config_help.pack(anchor="w", pady=5)
        
        # Initialize UI state
        self.toggle_lights_settings()
        self.toggle_button_settings()
        self.toggle_advanced_settings()
    
    def toggle_lights_settings(self):
        """Show or hide lighting settings based on checkbox state."""
        if self.use_lights_var.get():
            self.lights_frame.pack(fill="x", pady=10)
        else:
            self.lights_frame.pack_forget()
    
    def toggle_button_settings(self):
        """Show or hide button lighting settings based on checkbox state."""
        if self.use_button_lights_var.get():
            self.button_settings_frame.pack(fill="x", pady=5)
        else:
            self.button_settings_frame.pack_forget()
    
    def toggle_advanced_settings(self):
        """Show or hide advanced lighting settings based on checkbox state."""
        if self.advanced_var.get():
            self.advanced_frame.pack(fill="x", pady=5)
        else:
            self.advanced_frame.pack_forget()
    
    def choose_color(self, color_var):
        """Open a color chooser dialog and set the selected color.
        
        Args:
            color_var: The StringVar to update with the selected color
        """
        color = colorchooser.askcolor(initialcolor=color_var.get())
        if color[1]:
            color_var.set(color[1])
            
            # Update color preview
            if color_var == self.p1_color_var:
                self.p1_color_preview.configure(bg=color[1])
            elif color_var == self.p2_color_var:
                self.p2_color_preview.configure(bg=color[1])
            elif color_var == self.p3_color_var:
                self.p3_color_preview.configure(bg=color[1])
            elif color_var == self.p4_color_var:
                self.p4_color_preview.configure(bg=color[1])
    
    def browse_sketch(self):
        """Browse for an Arduino sketch file."""
        filetypes = [
            ("Arduino files", "*.ino"),
            ("All files", "*.*")
        ]
        
        initial_dir = os.path.dirname(self.sketch_var.get()) if self.sketch_var.get() else os.path.expanduser("~")
        
        file_path = filedialog.askopenfilename(
            title="Select Arduino Sketch",
            filetypes=filetypes,
            initialdir=initial_dir
        )
        
        if file_path:
            self.sketch_var.set(file_path)
    
    def browse_config(self):
        """Browse for a lighting configuration file."""
        filetypes = [
            ("JSON files", "*.json"),
            ("All files", "*.*")
        ]
        
        initial_dir = os.path.dirname(self.config_var.get()) if self.config_var.get() else os.path.expanduser("~")
        
        file_path = filedialog.askopenfilename(
            title="Select Lighting Configuration File",
            filetypes=filetypes,
            initialdir=initial_dir
        )
        
        if file_path:
            self.config_var.set(file_path)
    
    def validate(self):
        """Validate lighting configuration."""
        if not self.use_lights_var.get():
            return True
        
        # Validate port
        if not self.port_var.get().strip():
            messagebox.showerror(
                "Invalid Port", 
                "Please enter a COM port for the lighting controller."
            )
            return False
        
        # Validate sketch if provided
        sketch_path = self.sketch_var.get().strip()
        if sketch_path and not os.path.isfile(sketch_path):
            messagebox.showerror(
                "Invalid Sketch File", 
                "The specified Arduino sketch file does not exist."
            )
            return False
        
        # Validate advanced configuration file if provided
        if self.advanced_var.get():
            config_path = self.config_var.get().strip()
            if config_path and not os.path.isfile(config_path):
                messagebox.showerror(
                    "Invalid Configuration File", 
                    "The specified lighting configuration file does not exist."
                )
                return False
        
        return True
    
    def save_data(self):
        """Save lighting configuration to the user config."""
        if self.use_lights_var.get():
            lights_config = {
                "enabled": True,
                "system": self.system_var.get(),
                "brightness": self.brightness_var.get(),
                "default_animation": self.anim_var.get(),
                "cabinet": {
                    "has_marquee": self.use_marquee_var.get(),
                    "has_cp_lighting": self.use_cp_var.get(),
                    "has_speaker_lighting": self.use_speakers_var.get()
                }
            }
            
            # Add arduino specific settings
            if self.system_var.get() == "arduino":
                lights_config["arduino"] = {
                    "port": self.port_var.get().strip(),
                    "num_leds": self.leds_var.get()
                }
                
                if self.sketch_var.get().strip():
                    lights_config["arduino"]["sketch"] = self.sketch_var.get().strip()
            
            # Add button lighting if enabled
            if self.use_button_lights_var.get():
                lights_config["button_lighting"] = {
                    "enabled": True,
                    "player_colors": [
                        self.p1_color_var.get(),
                        self.p2_color_var.get(),
                        self.p3_color_var.get(),
                        self.p4_color_var.get()
                    ]
                }
            
            # Add advanced configuration if enabled
            if self.advanced_var.get() and self.config_var.get().strip():
                lights_config["custom_config"] = self.config_var.get().strip()
            
            self.app.user_config["lighting"] = lights_config
        else:
            # Just set lighting as disabled
            self.app.user_config["lighting"] = {"enabled": False} 