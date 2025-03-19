"""
Display configuration page for the Arcade Station Installer
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from .base_page import BasePage

class DisplayConfigPage(BasePage):
    """Page for configuring display and marquee settings."""
    
    def __init__(self, container, app):
        """Initialize the display configuration page."""
        # Initialize monitor count before calling super().__init__
        # because the base class will call create_widgets()
        self.monitor_count = self.get_monitor_count_safe(app)
        
        # Now call the parent constructor which will call create_widgets()
        super().__init__(container, app)
        self.set_title(
            "Display Configuration",
            "Configure dynamic marquee and display settings"
        )
    
    def get_monitor_count_safe(self, app):
        """Get the number of monitors connected to the system safely.
        This method is called before __init__ is completed, so we pass app as a parameter.
        """
        try:
            # Try more advanced detection if available
            try:
                import screeninfo
                monitors = screeninfo.get_monitors()
                return len(monitors)
            except (ImportError, AttributeError):
                # Fallback: assume at least one monitor
                return max(1, app.install_manager.get_monitor_count())
                
        except Exception:
            # Default to 1 if detection fails
            return 1
    
    def get_monitor_count(self):
        """Get the number of monitors connected to the system."""
        try:
            # Use Tkinter's winfo_screenwidth/height for basic detection
            root = self.app.root
            width = root.winfo_screenwidth()
            height = root.winfo_screenheight()
            
            # Try more advanced detection if available
            try:
                import screeninfo
                monitors = screeninfo.get_monitors()
                return len(monitors)
            except (ImportError, AttributeError):
                # Fallback: assume at least one monitor
                return max(1, self.app.install_manager.get_monitor_count())
                
        except Exception:
            # Default to 1 if detection fails
            return 1
    
    def create_widgets(self):
        """Create page-specific widgets."""
        # Make absolutely sure monitor_count is set
        if not hasattr(self, 'monitor_count') or self.monitor_count < 1:
            self.monitor_count = 1
            
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Dynamic Marquee explanation
        explanation = ttk.Label(
            main_frame,
            text="Arcade Station can display game banners and artwork on a secondary monitor, "
                 "creating a dynamic marquee effect that changes based on the selected game.",
            wraplength=500,
            justify="left"
        )
        explanation.pack(anchor="w", pady=(0, 20))
        
        # Enable Dynamic Marquee checkbox
        self.enable_marquee_var = tk.BooleanVar(value=True)
        enable_marquee = ttk.Checkbutton(
            main_frame,
            text="Enable Dynamic Marquee",
            variable=self.enable_marquee_var,
            command=self.toggle_marquee_options
        )
        enable_marquee.pack(anchor="w", pady=(0, 10))
        
        # Marquee settings frame
        self.marquee_settings = ttk.LabelFrame(
            main_frame,
            text="Marquee Settings",
            padding=(10, 5)
        )
        
        # Monitor selection
        monitor_frame = ttk.Frame(self.marquee_settings)
        monitor_frame.pack(fill="x", pady=5)
        
        monitor_label = ttk.Label(
            monitor_frame,
            text="Marquee Monitor:",
            width=15
        )
        monitor_label.pack(side="left", padx=(0, 5))
        
        self.monitor_var = tk.StringVar(value="1")
        
        # Generate monitor values
        monitor_values = [str(i+1) for i in range(self.monitor_count)]
        if not monitor_values:  # Ensure there's at least one value
            monitor_values = ["1"]
            
        monitor_options = ttk.Combobox(
            monitor_frame,
            textvariable=self.monitor_var,
            values=monitor_values,
            width=5,
            state="readonly"
        )
        monitor_options.pack(side="left")
        
        monitor_help = ttk.Label(
            monitor_frame,
            text=f"(Detected {self.monitor_count} monitor{'s' if self.monitor_count != 1 else ''})",
            font=("Arial", 9),
            foreground="#555555"
        )
        monitor_help.pack(side="left", padx=10)
        
        # Default background color
        color_frame = ttk.Frame(self.marquee_settings)
        color_frame.pack(fill="x", pady=5)
        
        color_label = ttk.Label(
            color_frame,
            text="Background Color:",
            width=15
        )
        color_label.pack(side="left", padx=(0, 5))
        
        self.color_var = tk.StringVar(value="black")
        
        color_options = ttk.Combobox(
            color_frame,
            textvariable=self.color_var,
            values=["black", "white", "gray", "blue", "red", "green"],
            width=10,
            state="readonly"
        )
        color_options.pack(side="left")
        
        # Default marquee image
        image_frame = ttk.Frame(self.marquee_settings)
        image_frame.pack(fill="x", pady=5)
        
        image_label = ttk.Label(
            image_frame,
            text="Default Image:",
            width=15
        )
        image_label.pack(side="left", padx=(0, 5))
        
        self.image_var = tk.StringVar()
        
        image_entry = ttk.Entry(
            image_frame,
            textvariable=self.image_var,
            width=30
        )
        image_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_button = ttk.Button(
            image_frame,
            text="Browse...",
            command=self.browse_image
        )
        browse_button.pack(side="right")
        
        # ITGMania integration
        self.itgmania_frame = ttk.LabelFrame(
            main_frame,
            text="ITGMania Integration",
            padding=(10, 5)
        )
        
        itgmania_explanation = ttk.Label(
            self.itgmania_frame,
            text="Arcade Station can integrate with ITGMania to display song-specific "
                 "information on the marquee display.",
            wraplength=450,
            justify="left"
        )
        itgmania_explanation.pack(anchor="w", pady=5)
        
        self.enable_itgmania_var = tk.BooleanVar(value=True)
        enable_itgmania = ttk.Checkbutton(
            self.itgmania_frame,
            text="Enable ITGMania marquee integration",
            variable=self.enable_itgmania_var
        )
        enable_itgmania.pack(anchor="w", pady=5)
        
        # Set initial state
        self.toggle_marquee_options()
    
    def toggle_marquee_options(self):
        """Show or hide marquee options based on checkbox state."""
        if self.enable_marquee_var.get():
            self.marquee_settings.pack(fill="x", pady=10)
            self.itgmania_frame.pack(fill="x", pady=10)
        else:
            self.marquee_settings.pack_forget()
            self.itgmania_frame.pack_forget()
    
    def browse_image(self):
        """Open a file browser dialog for selecting the default marquee image."""
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
            ("All files", "*.*")
        ]
        
        image_path = filedialog.askopenfilename(
            title="Select Default Marquee Image",
            filetypes=filetypes
        )
        
        if image_path:
            self.image_var.set(image_path)
    
    def validate(self):
        """Validate display configuration settings."""
        if not self.enable_marquee_var.get():
            return True
        
        # Validate monitor selection
        try:
            monitor = int(self.monitor_var.get())
            if monitor < 1 or monitor > self.monitor_count:
                messagebox.showerror(
                    "Invalid Monitor", 
                    f"Please select a valid monitor (1-{self.monitor_count})."
                )
                return False
        except ValueError:
            messagebox.showerror(
                "Invalid Monitor", 
                "Please select a valid monitor number."
            )
            return False
        
        # Validate image path if provided
        image_path = self.image_var.get().strip()
        if image_path and not os.path.isfile(image_path):
            messagebox.showerror(
                "Invalid Image", 
                "The specified default image file does not exist."
            )
            return False
        
        return True
    
    def save_data(self):
        """Save display configuration settings."""
        self.app.user_config["use_dynamic_marquee"] = self.enable_marquee_var.get()
        
        if self.enable_marquee_var.get():
            self.app.user_config["marquee_monitor"] = int(self.monitor_var.get())
            self.app.user_config["marquee_background_color"] = self.color_var.get()
            
            if self.image_var.get().strip():
                self.app.user_config["default_marquee_image"] = self.image_var.get().strip()
            
            self.app.user_config["enable_itgmania_display"] = self.enable_itgmania_var.get() 