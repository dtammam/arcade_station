"""
Kiosk Mode configuration page for Windows
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
import platform
import hashlib

from .base_page import BasePage

class KioskModePage(BasePage):
    """Page for configuring Windows kiosk mode settings."""
    
    def __init__(self, container, app):
        """Initialize the kiosk mode page."""
        super().__init__(container, app)
        self.set_title(
            "Kiosk Mode Configuration",
            "Configure automatic login and startup"
        )
    
    def create_widgets(self):
        """Create page-specific widgets."""
        # Only relevant for Windows
        if platform.system().lower() != "windows":
            not_supported = ttk.Label(
                self.content_frame,
                text="Kiosk mode configuration is only available on Windows.",
                wraplength=500,
                justify="center"
            )
            not_supported.pack(expand=True, pady=50)
            return
        
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Explanation
        explanation = ttk.Label(
            main_frame,
            text="Kiosk Mode enables Arcade Station to function as a dedicated arcade "
                 "interface by configuring Windows to automatically log in and launch "
                 "Arcade Station at startup. This is ideal for arcade cabinets.",
            wraplength=500,
            justify="left"
        )
        explanation.pack(anchor="w", pady=(0, 20))
        
        # Enable Kiosk Mode checkbox
        self.enable_kiosk_var = tk.BooleanVar(value=False)
        enable_kiosk = ttk.Checkbutton(
            main_frame,
            text="Enable Kiosk Mode",
            variable=self.enable_kiosk_var,
            command=self.toggle_kiosk_options
        )
        enable_kiosk.pack(anchor="w", pady=(0, 10))
        
        # Kiosk settings frame (will be shown/hidden based on checkbox)
        self.kiosk_settings = ttk.LabelFrame(
            main_frame,
            text="Kiosk Mode Settings",
            padding=(10, 5)
        )
        
        # Auto-login settings
        autologin_frame = ttk.Frame(self.kiosk_settings)
        autologin_frame.pack(fill="x", pady=5)
        
        self.auto_login_var = tk.BooleanVar(value=True)
        auto_login = ttk.Checkbutton(
            autologin_frame,
            text="Enable Auto-login",
            variable=self.auto_login_var
        )
        auto_login.pack(anchor="w")
        
        username_label = ttk.Label(
            autologin_frame,
            text="Username:",
            width=15
        )
        username_label.pack(side="left", padx=(0, 5))
        
        self.username_var = tk.StringVar(value=os.environ.get("USERNAME", ""))
        username_entry = ttk.Entry(
            autologin_frame,
            textvariable=self.username_var,
            width=30
        )
        username_entry.pack(side="left", fill="x", expand=True)
        
        # Password entry
        password_frame = ttk.Frame(self.kiosk_settings)
        password_frame.pack(fill="x", pady=5)
        
        password_label = ttk.Label(
            password_frame,
            text="Password:",
            width=15
        )
        password_label.pack(side="left", padx=(0, 5))
        
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(
            password_frame,
            textvariable=self.password_var,
            show="*",
            width=30
        )
        password_entry.pack(side="left", fill="x", expand=True)
        
        # Additional kiosk options
        options_frame = ttk.Frame(self.kiosk_settings)
        options_frame.pack(fill="x", pady=5)
        
        self.disable_task_manager_var = tk.BooleanVar(value=True)
        disable_task_manager = ttk.Checkbutton(
            options_frame,
            text="Disable Task Manager",
            variable=self.disable_task_manager_var
        )
        disable_task_manager.pack(anchor="w")
        
        self.hide_cursor_var = tk.BooleanVar(value=True)
        hide_cursor = ttk.Checkbutton(
            options_frame,
            text="Hide Mouse Cursor",
            variable=self.hide_cursor_var
        )
        hide_cursor.pack(anchor="w")
        
        # Explorer shell options
        shell_frame = ttk.Frame(self.kiosk_settings)
        shell_frame.pack(fill="x", pady=10)
        
        self.replace_shell_var = tk.BooleanVar(value=True)
        replace_shell = ttk.Checkbutton(
            shell_frame,
            text="Replace Windows Explorer with Arcade Station",
            variable=self.replace_shell_var
        )
        replace_shell.pack(anchor="w")
        
        shell_info = ttk.Label(
            shell_frame,
            text="This will replace the Windows shell (explorer.exe) with Arcade Station, "
                 "providing a dedicated arcade experience without the standard Windows desktop.",
            wraplength=450,
            justify="left",
            font=("Arial", 9),
            foreground="#555555"
        )
        shell_info.pack(anchor="w", padx=(25, 0))
        
        # Security warning
        warning_frame = ttk.Frame(main_frame)
        warning_frame.pack(fill="x", pady=10)
        
        security_warning = ttk.Label(
            warning_frame,
            text="Warning: Enabling auto-login will use your password to configure the Windows registry. "
                 "The password is used only during installation and is not stored in the application. "
                 "For security, consider using a dedicated account for your arcade system.",
            wraplength=500,
            foreground="red",
            justify="left"
        )
        security_warning.pack(anchor="w")
        
        # Initial state - hide kiosk settings by default
        self.toggle_kiosk_options()
    
    def toggle_kiosk_options(self):
        """Show or hide kiosk options based on checkbox state."""
        if self.enable_kiosk_var.get():
            self.kiosk_settings.pack(fill="x", pady=10)
        else:
            self.kiosk_settings.pack_forget()
    
    def validate(self):
        """Validate kiosk mode settings."""
        if not self.enable_kiosk_var.get():
            return True
        
        if not self.username_var.get().strip():
            messagebox.showerror(
                "Invalid Input", 
                "Please enter a username for auto-login."
            )
            return False
        
        # Password is optional but recommended
        if not self.password_var.get():
            result = messagebox.askyesno(
                "Confirm No Password", 
                "You haven't entered a password for auto-login. This will create "
                "an unsecured auto-login. Continue anyway?"
            )
            if not result:
                return False
        
        return True
    
    def save_data(self):
        """Save kiosk mode settings."""
        self.app.user_config["enable_kiosk_mode"] = self.enable_kiosk_var.get()
        
        if self.enable_kiosk_var.get():
            self.app.user_config["kiosk_username"] = self.username_var.get().strip()
            
            # Temporarily store password for Windows registry setup during installation
            # This will be used once during installation and then discarded
            if self.password_var.get() and self.auto_login_var.get():
                self.app.user_config["kiosk_password"] = self.password_var.get()
            
            self.app.user_config["kiosk_auto_login"] = self.auto_login_var.get()
            self.app.user_config["kiosk_disable_task_manager"] = self.disable_task_manager_var.get()
            self.app.user_config["kiosk_hide_cursor"] = self.hide_cursor_var.get()
            self.app.user_config["kiosk_replace_shell"] = self.replace_shell_var.get()
            
        return True 