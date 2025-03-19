"""
Utility configuration page for the Arcade Station Installer
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import hashlib

from .base_page import BasePage

class UtilityConfigPage(BasePage):
    """Page for configuring system utilities and maintenance tools."""
    
    def __init__(self, container, app):
        """Initialize the utility configuration page."""
        super().__init__(container, app)
        self.set_title(
            "Utilities Setup",
            "Configure system utilities and maintenance tools"
        )
    
    def create_widgets(self):
        """Create page-specific widgets."""
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Introduction
        intro_text = ttk.Label(
            main_frame,
            text="Configure system utilities and maintenance tools for your Arcade Station. "
                 "These tools help maintain your system and provide additional functionality.",
            wraplength=500,
            justify="left"
        )
        intro_text.pack(anchor="w", pady=(0, 15))
        
        # System utilities frame
        system_frame = ttk.LabelFrame(
            main_frame,
            text="System Utilities",
            padding=(10, 5)
        )
        system_frame.pack(fill="x", pady=10)
        
        # Enable system utilities
        self.enable_system_var = tk.BooleanVar(value=True)
        enable_system = ttk.Checkbutton(
            system_frame,
            text="Enable system utilities",
            variable=self.enable_system_var
        )
        enable_system.pack(anchor="w", pady=5)
        
        # Auto updates
        self.auto_updates_var = tk.BooleanVar(value=True)
        auto_updates = ttk.Checkbutton(
            system_frame,
            text="Check for updates automatically",
            variable=self.auto_updates_var
        )
        auto_updates.pack(anchor="w", padx=20, pady=2)
        
        # System monitoring
        self.system_monitoring_var = tk.BooleanVar(value=True)
        system_monitoring = ttk.Checkbutton(
            system_frame,
            text="Enable system monitoring (CPU, RAM, temperature)",
            variable=self.system_monitoring_var
        )
        system_monitoring.pack(anchor="w", padx=20, pady=2)
        
        # Error reporting
        self.error_reporting_var = tk.BooleanVar(value=True)
        error_reporting = ttk.Checkbutton(
            system_frame,
            text="Enable automatic error reporting",
            variable=self.error_reporting_var
        )
        error_reporting.pack(anchor="w", padx=20, pady=2)
        
        # Custom log directory
        log_frame = ttk.Frame(system_frame)
        log_frame.pack(fill="x", padx=20, pady=2)
        
        log_label = ttk.Label(
            log_frame,
            text="Custom Log Directory:",
            width=20
        )
        log_label.pack(side="left", padx=(0, 5))
        
        self.log_dir_var = tk.StringVar()
        log_dir_entry = ttk.Entry(
            log_frame,
            textvariable=self.log_dir_var,
            width=40
        )
        log_dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_log_button = ttk.Button(
            log_frame,
            text="Browse...",
            command=self.browse_log_dir
        )
        browse_log_button.pack(side="right")
        
        # Backup frame
        backup_frame = ttk.LabelFrame(
            main_frame,
            text="Backup and Restore",
            padding=(10, 5)
        )
        backup_frame.pack(fill="x", pady=10)
        
        # Enable backups
        self.enable_backup_var = tk.BooleanVar(value=True)
        enable_backup = ttk.Checkbutton(
            backup_frame,
            text="Enable automatic backups",
            variable=self.enable_backup_var,
            command=self.toggle_backup_options
        )
        enable_backup.pack(anchor="w", pady=5)
        
        # Backup options frame
        self.backup_options_frame = ttk.Frame(backup_frame)
        self.backup_options_frame.pack(fill="x", pady=5)
        
        # Backup frequency
        frequency_frame = ttk.Frame(self.backup_options_frame)
        frequency_frame.pack(fill="x", padx=20, pady=2)
        
        frequency_label = ttk.Label(
            frequency_frame,
            text="Backup Frequency:",
            width=20
        )
        frequency_label.pack(side="left", padx=(0, 5))
        
        self.frequency_var = tk.StringVar(value="weekly")
        frequency_combo = ttk.Combobox(
            frequency_frame,
            textvariable=self.frequency_var,
            values=["daily", "weekly", "monthly", "manual"],
            width=15
        )
        frequency_combo.pack(side="left")
        frequency_combo.state(["readonly"])
        
        # Backup directory
        backup_dir_frame = ttk.Frame(self.backup_options_frame)
        backup_dir_frame.pack(fill="x", padx=20, pady=2)
        
        backup_dir_label = ttk.Label(
            backup_dir_frame,
            text="Backup Directory:",
            width=20
        )
        backup_dir_label.pack(side="left", padx=(0, 5))
        
        self.backup_dir_var = tk.StringVar()
        backup_dir_entry = ttk.Entry(
            backup_dir_frame,
            textvariable=self.backup_dir_var,
            width=40
        )
        backup_dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_backup_button = ttk.Button(
            backup_dir_frame,
            text="Browse...",
            command=self.browse_backup_dir
        )
        browse_backup_button.pack(side="right")
        
        # Keep backups
        keep_frame = ttk.Frame(self.backup_options_frame)
        keep_frame.pack(fill="x", padx=20, pady=2)
        
        keep_label = ttk.Label(
            keep_frame,
            text="Keep Backups:",
            width=20
        )
        keep_label.pack(side="left", padx=(0, 5))
        
        self.keep_var = tk.IntVar(value=5)
        keep_spinbox = ttk.Spinbox(
            keep_frame,
            from_=1,
            to=20,
            textvariable=self.keep_var,
            width=5
        )
        keep_spinbox.pack(side="left")
        
        # Maintenance tools frame
        tools_frame = ttk.LabelFrame(
            main_frame,
            text="Maintenance Tools",
            padding=(10, 5)
        )
        tools_frame.pack(fill="x", pady=10)
        
        # Tools to install
        tools_label = ttk.Label(
            tools_frame,
            text="Select maintenance tools to install:",
            font=("Arial", 10, "bold")
        )
        tools_label.pack(anchor="w", pady=5)
        
        # ROM validation tool
        self.rom_validator_var = tk.BooleanVar(value=True)
        rom_validator = ttk.Checkbutton(
            tools_frame,
            text="ROM Validator - Check ROM integrity and verify MD5 checksums",
            variable=self.rom_validator_var
        )
        rom_validator.pack(anchor="w", padx=20, pady=2)
        
        # Input tester
        self.input_tester_var = tk.BooleanVar(value=True)
        input_tester = ttk.Checkbutton(
            tools_frame,
            text="Input Tester - Test and calibrate arcade controls and gamepads",
            variable=self.input_tester_var
        )
        input_tester.pack(anchor="w", padx=20, pady=2)
        
        # System cleaner
        self.system_cleaner_var = tk.BooleanVar(value=True)
        system_cleaner = ttk.Checkbutton(
            tools_frame,
            text="System Cleaner - Remove temporary files and optimize performance",
            variable=self.system_cleaner_var
        )
        system_cleaner.pack(anchor="w", padx=20, pady=2)
        
        # Config editor
        self.config_editor_var = tk.BooleanVar(value=True)
        config_editor = ttk.Checkbutton(
            tools_frame,
            text="Configuration Editor - Advanced editor for system configuration files",
            variable=self.config_editor_var
        )
        config_editor.pack(anchor="w", padx=20, pady=2)
        
        # Media manager
        self.media_manager_var = tk.BooleanVar(value=True)
        media_manager = ttk.Checkbutton(
            tools_frame,
            text="Media Manager - Manage game banners, marquees and videos",
            variable=self.media_manager_var
        )
        media_manager.pack(anchor="w", padx=20, pady=2)
        
        # Quick service menu
        self.quick_service_var = tk.BooleanVar(value=True)
        quick_service = ttk.Checkbutton(
            tools_frame,
            text="Quick Service Menu - Add a service menu accessible in-game",
            variable=self.quick_service_var
        )
        quick_service.pack(anchor="w", padx=20, pady=2)
        
        # Advanced options
        advanced_frame = ttk.LabelFrame(
            main_frame,
            text="Advanced Options",
            padding=(10, 5)
        )
        advanced_frame.pack(fill="x", pady=10)
        
        # Startup password
        startup_frame = ttk.Frame(advanced_frame)
        startup_frame.pack(fill="x", pady=5)
        
        self.use_password_var = tk.BooleanVar(value=False)
        use_password = ttk.Checkbutton(
            startup_frame,
            text="Require password for maintenance mode:",
            variable=self.use_password_var,
            command=self.toggle_password
        )
        use_password.pack(side="left", padx=(0, 5))
        
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(
            startup_frame,
            textvariable=self.password_var,
            width=20,
            show="*"
        )
        self.password_entry.pack(side="right", padx=5)
        
        # Custom maintenance key
        key_frame = ttk.Frame(advanced_frame)
        key_frame.pack(fill="x", pady=5)
        
        key_label = ttk.Label(
            key_frame,
            text="Maintenance Mode Key:"
        )
        key_label.pack(side="left", padx=(0, 5))
        
        self.key_var = tk.StringVar(value="F10")
        key_combo = ttk.Combobox(
            key_frame,
            textvariable=self.key_var,
            values=["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "Tab", "Escape"],
            width=10
        )
        key_combo.pack(side="left")
        key_combo.state(["readonly"])
        
        # Custom scripts frame
        scripts_frame = ttk.LabelFrame(
            main_frame,
            text="Custom Scripts",
            padding=(10, 5)
        )
        scripts_frame.pack(fill="x", pady=10)
        
        # Add custom scripts
        self.use_scripts_var = tk.BooleanVar(value=False)
        use_scripts = ttk.Checkbutton(
            scripts_frame,
            text="Add custom maintenance scripts",
            variable=self.use_scripts_var,
            command=self.toggle_scripts
        )
        use_scripts.pack(anchor="w", pady=5)
        
        # Scripts options frame
        self.scripts_frame = ttk.Frame(scripts_frame)
        
        # Script folder
        script_dir_frame = ttk.Frame(self.scripts_frame)
        script_dir_frame.pack(fill="x", pady=5)
        
        script_dir_label = ttk.Label(
            script_dir_frame,
            text="Scripts Directory:",
            width=20
        )
        script_dir_label.pack(side="left", padx=(0, 5))
        
        self.script_dir_var = tk.StringVar()
        script_dir_entry = ttk.Entry(
            script_dir_frame,
            textvariable=self.script_dir_var,
            width=40
        )
        script_dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_script_button = ttk.Button(
            script_dir_frame,
            text="Browse...",
            command=self.browse_script_dir
        )
        browse_script_button.pack(side="right")
        
        # Initialize UI state
        self.toggle_backup_options()
        self.toggle_password()
        self.toggle_scripts()
    
    def toggle_backup_options(self):
        """Show or hide backup options based on checkbox state."""
        if self.enable_backup_var.get():
            self.backup_options_frame.pack(fill="x", pady=5)
        else:
            self.backup_options_frame.pack_forget()
    
    def toggle_password(self):
        """Enable or disable password entry based on checkbox state."""
        if self.use_password_var.get():
            self.password_entry.configure(state="normal")
        else:
            self.password_entry.configure(state="disabled")
    
    def toggle_scripts(self):
        """Show or hide custom scripts options based on checkbox state."""
        if self.use_scripts_var.get():
            self.scripts_frame.pack(fill="x", pady=5)
        else:
            self.scripts_frame.pack_forget()
    
    def browse_log_dir(self):
        """Browse for a log directory."""
        initial_dir = self.log_dir_var.get() if self.log_dir_var.get() else os.path.expanduser("~")
        
        dir_path = filedialog.askdirectory(
            title="Select Log Directory",
            initialdir=initial_dir
        )
        
        if dir_path:
            self.log_dir_var.set(dir_path)
    
    def browse_backup_dir(self):
        """Browse for a backup directory."""
        initial_dir = self.backup_dir_var.get() if self.backup_dir_var.get() else os.path.expanduser("~")
        
        dir_path = filedialog.askdirectory(
            title="Select Backup Directory",
            initialdir=initial_dir
        )
        
        if dir_path:
            self.backup_dir_var.set(dir_path)
    
    def browse_script_dir(self):
        """Browse for a scripts directory."""
        initial_dir = self.script_dir_var.get() if self.script_dir_var.get() else os.path.expanduser("~")
        
        dir_path = filedialog.askdirectory(
            title="Select Scripts Directory",
            initialdir=initial_dir
        )
        
        if dir_path:
            self.script_dir_var.set(dir_path)
    
    def validate(self):
        """Validate utility configuration."""
        # Validate custom log directory if provided
        log_dir = self.log_dir_var.get().strip()
        if log_dir and not os.path.isdir(log_dir):
            messagebox.showerror(
                "Invalid Log Directory", 
                "The specified log directory does not exist. Please create it first."
            )
            return False
        
        # Validate backup configuration
        if self.enable_backup_var.get():
            backup_dir = self.backup_dir_var.get().strip()
            if not backup_dir:
                messagebox.showerror(
                    "Backup Directory Required", 
                    "Please specify a backup directory."
                )
                return False
            
            if not os.path.isdir(backup_dir):
                if messagebox.askyesno(
                    "Create Directory?", 
                    f"The backup directory '{backup_dir}' does not exist. Would you like to create it?"
                ):
                    try:
                        os.makedirs(backup_dir, exist_ok=True)
                    except Exception as e:
                        messagebox.showerror(
                            "Error Creating Directory", 
                            f"Failed to create backup directory: {str(e)}"
                        )
                        return False
                else:
                    return False
        
        # Validate custom scripts directory
        if self.use_scripts_var.get():
            script_dir = self.script_dir_var.get().strip()
            if not script_dir:
                messagebox.showerror(
                    "Scripts Directory Required", 
                    "Please specify a directory containing your custom scripts."
                )
                return False
            
            if not os.path.isdir(script_dir):
                messagebox.showerror(
                    "Invalid Scripts Directory", 
                    "The specified scripts directory does not exist."
                )
                return False
        
        # Validate password if enabled
        if self.use_password_var.get() and not self.password_var.get().strip():
            messagebox.showerror(
                "Password Required", 
                "Please enter a password for maintenance mode."
            )
            return False
        
        return True
    
    def save_data(self):
        """Save utility configuration to the user config."""
        utilities_config = {
            "system": {
                "enabled": self.enable_system_var.get(),
                "auto_updates": self.auto_updates_var.get(),
                "system_monitoring": self.system_monitoring_var.get(),
                "error_reporting": self.error_reporting_var.get()
            },
            "maintenance_tools": {
                "rom_validator": self.rom_validator_var.get(),
                "input_tester": self.input_tester_var.get(),
                "system_cleaner": self.system_cleaner_var.get(),
                "config_editor": self.config_editor_var.get(),
                "media_manager": self.media_manager_var.get(),
                "quick_service": self.quick_service_var.get()
            },
            "advanced": {
                "maintenance_key": self.key_var.get()
            }
        }
        
        # Add custom log directory if provided
        log_dir = self.log_dir_var.get().strip()
        if log_dir:
            utilities_config["system"]["log_directory"] = log_dir
        
        # Add backup configuration if enabled
        if self.enable_backup_var.get():
            utilities_config["backup"] = {
                "enabled": True,
                "frequency": self.frequency_var.get(),
                "directory": self.backup_dir_var.get().strip(),
                "keep_backups": self.keep_var.get()
            }
        else:
            utilities_config["backup"] = {"enabled": False}
        
        # Add password if enabled
        if self.use_password_var.get():
            # Generate a salt and hash the password
            salt = os.urandom(16).hex()
            password = self.password_var.get()
            hashed_pw = hashlib.sha256((password + salt).encode()).hexdigest()
            
            # Store the salt and hash, not the plaintext password
            utilities_config["advanced"]["maintenance_password_hash"] = hashed_pw
            utilities_config["advanced"]["maintenance_password_salt"] = salt
        
        # Add custom scripts if enabled
        if self.use_scripts_var.get():
            utilities_config["custom_scripts"] = {
                "enabled": True,
                "directory": self.script_dir_var.get().strip()
            }
        
        self.app.user_config["utilities"] = utilities_config 