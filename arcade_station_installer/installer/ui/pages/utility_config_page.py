"""
Utility configuration page for the Arcade Station Installer
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import platform

from .base_page import BasePage

class UtilityConfigPage(BasePage):
    """Page for configuring system utilities for Arcade Station."""
    
    def __init__(self, container, app):
        """Initialize the utility configuration page."""
        self.is_windows = platform.system() == "Windows"
        super().__init__(container, app)
        self.set_title(
            "Utilities Setup",
            "Configure utilities for your Arcade Station"
        )
    
    def create_widgets(self):
        """Create page-specific widgets."""
        # Create a canvas with scrollbar for the content
        canvas = tk.Canvas(self.content_frame)
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        main_frame = ttk.Frame(self.scrollable_frame)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Introduction
        intro_text = ttk.Label(
            main_frame,
            text="Configure utilities for your Arcade Station. These tools enhance your gaming experience.",
            wraplength=500,
            justify="left"
        )
        intro_text.pack(anchor="w", pady=(0, 15))
        
        # Lights configuration (Windows only)
        if self.is_windows:
            self.create_lights_section(main_frame)
        
        # Streaming configuration
        self.create_streaming_section(main_frame)
        
        # VPN configuration (Windows only)
        if self.is_windows:
            self.create_vpn_section(main_frame)
        
        # OSD configuration (Windows only)
        if self.is_windows:
            self.create_osd_section(main_frame)
            
        # Initialize visibility of option frames
        self.toggle_lights_options()
        self.toggle_streaming_options()
        self.toggle_webcam_options()
        self.toggle_vpn_options()
    
    def create_lights_section(self, parent):
        """Create the lights configuration section."""
        lights_frame = ttk.LabelFrame(
            parent,
            text="Lights Configuration (Windows Only)",
            padding=(10, 5)
        )
        lights_frame.pack(fill="x", pady=10)
        
        # Enable lights management - unchecked by default
        self.enable_lights_var = tk.BooleanVar(value=False)
        enable_lights = ttk.Checkbutton(
            lights_frame,
            text="Do you want Arcade Station to manage your lights? This is useful for things like litboards, as you'll need to reset them when closing your games.",
            variable=self.enable_lights_var,
            command=self.toggle_lights_options
        )
        enable_lights.pack(anchor="w", pady=5)
        
        # Lights options frame
        self.lights_options_frame = ttk.Frame(lights_frame)
        
        # Lights reset program
        reset_frame = ttk.Frame(self.lights_options_frame)
        reset_frame.pack(fill="x", pady=5)
        
        reset_label = ttk.Label(
            reset_frame,
            text="Lights reset program:",
            width=20
        )
        reset_label.pack(side="left", padx=(0, 5))
        
        self.lights_reset_var = tk.StringVar(value="../bin/windows/LightsTest.exe")
        reset_entry = ttk.Entry(
            reset_frame,
            textvariable=self.lights_reset_var,
            width=40
        )
        reset_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_reset_button = ttk.Button(
            reset_frame,
            text="Browse...",
            command=self.browse_lights_reset
        )
        browse_reset_button.pack(side="right")
        
        # Lights MAME executable
        mame_frame = ttk.Frame(self.lights_options_frame)
        mame_frame.pack(fill="x", pady=5)
        
        mame_label = ttk.Label(
            mame_frame,
            text="Lights MAME executable:",
            width=20
        )
        mame_label.pack(side="left", padx=(0, 5))
        
        self.lights_mame_var = tk.StringVar(value="../bin/windows/mame2lit.exe")
        mame_entry = ttk.Entry(
            mame_frame,
            textvariable=self.lights_mame_var,
            width=40
        )
        mame_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_mame_button = ttk.Button(
            mame_frame,
            text="Browse...",
            command=self.browse_lights_mame
        )
        browse_mame_button.pack(side="right")
    
    def create_streaming_section(self, parent):
        """Create the streaming configuration section."""
        streaming_frame = ttk.LabelFrame(
            parent,
            text="Streaming Configuration",
            padding=(10, 5)
        )
        streaming_frame.pack(fill="x", pady=10)
        
        # Enable streaming
        self.enable_streaming_var = tk.BooleanVar(value=False)
        enable_streaming = ttk.Checkbutton(
            streaming_frame,
            text="Do you want Arcade Station to help kickoff your streaming session?",
            variable=self.enable_streaming_var,
            command=self.toggle_streaming_options
        )
        enable_streaming.pack(anchor="w", pady=5)
        
        # Streaming options frame
        self.streaming_options_frame = ttk.Frame(streaming_frame)
        
        # Webcam management
        webcam_frame = ttk.Frame(self.streaming_options_frame)
        webcam_frame.pack(fill="x", pady=5)
        
        self.enable_webcam_var = tk.BooleanVar(value=False)
        enable_webcam = ttk.Checkbutton(
            webcam_frame,
            text="Do you need a webcam management app to start before streaming?",
            variable=self.enable_webcam_var,
            command=self.toggle_webcam_options
        )
        enable_webcam.pack(anchor="w", pady=5)
        
        # Webcam executable frame
        self.webcam_options_frame = ttk.Frame(self.streaming_options_frame)
        
        webcam_exe_frame = ttk.Frame(self.webcam_options_frame)
        webcam_exe_frame.pack(fill="x", pady=5)
        
        webcam_exe_label = ttk.Label(
            webcam_exe_frame,
            text="Webcam app:",
            width=20
        )
        webcam_exe_label.pack(side="left", padx=(0, 5))
        
        self.webcam_exe_var = tk.StringVar(value="C:/Program Files/Logitech/LogiCapture/bin/LogiCapture.exe")
        webcam_exe_entry = ttk.Entry(
            webcam_exe_frame,
            textvariable=self.webcam_exe_var,
            width=40
        )
        webcam_exe_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_webcam_button = ttk.Button(
            webcam_exe_frame,
            text="Browse...",
            command=self.browse_webcam_exe
        )
        browse_webcam_button.pack(side="right")
        
        # OBS executable
        obs_frame = ttk.Frame(self.streaming_options_frame)
        obs_frame.pack(fill="x", pady=5)
        
        obs_label = ttk.Label(
            obs_frame,
            text="OBS executable:",
            width=20
        )
        obs_label.pack(side="left", padx=(0, 5))
        
        self.obs_exe_var = tk.StringVar(value="C:/Program Files/obs-studio/bin/64bit/obs64.exe")
        obs_entry = ttk.Entry(
            obs_frame,
            textvariable=self.obs_exe_var,
            width=40
        )
        obs_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_obs_button = ttk.Button(
            obs_frame,
            text="Browse...",
            command=self.browse_obs_exe
        )
        browse_obs_button.pack(side="right")
        
        # OBS arguments
        args_frame = ttk.Frame(self.streaming_options_frame)
        args_frame.pack(fill="x", pady=5)
        
        args_label = ttk.Label(
            args_frame,
            text="OBS arguments:",
            width=20
        )
        args_label.pack(side="left", padx=(0, 5))
        
        self.obs_args_var = tk.StringVar(value="--startstreaming --disable-shutdown-check")
        args_entry = ttk.Entry(
            args_frame,
            textvariable=self.obs_args_var,
            width=40
        )
        args_entry.pack(side="left", fill="x", expand=True)
    
    def create_vpn_section(self, parent):
        """Create the VPN configuration section."""
        vpn_frame = ttk.LabelFrame(
            parent,
            text="VPN Configuration (Windows Only)",
            padding=(10, 5)
        )
        vpn_frame.pack(fill="x", pady=10)
        
        # Enable VPN
        self.enable_vpn_var = tk.BooleanVar(value=False)
        enable_vpn = ttk.Checkbutton(
            vpn_frame,
            text="Do you want Arcade Station to automatically connect your VPN?",
            variable=self.enable_vpn_var,
            command=self.toggle_vpn_options
        )
        enable_vpn.pack(anchor="w", pady=5)
        
        # VPN options frame
        self.vpn_options_frame = ttk.Frame(vpn_frame)
        
        # VPN install directory
        vpn_dir_frame = ttk.Frame(self.vpn_options_frame)
        vpn_dir_frame.pack(fill="x", pady=5)
        
        vpn_dir_label = ttk.Label(
            vpn_dir_frame,
            text="VPN install directory:",
            width=20
        )
        vpn_dir_label.pack(side="left", padx=(0, 5))
        
        self.vpn_dir_var = tk.StringVar(value="C:/Program Files/OpenVPN/bin")
        vpn_dir_entry = ttk.Entry(
            vpn_dir_frame,
            textvariable=self.vpn_dir_var,
            width=40
        )
        vpn_dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_vpn_dir_button = ttk.Button(
            vpn_dir_frame,
            text="Browse...",
            command=self.browse_vpn_dir
        )
        browse_vpn_dir_button.pack(side="right")
        
        # VPN application
        vpn_app_frame = ttk.Frame(self.vpn_options_frame)
        vpn_app_frame.pack(fill="x", pady=5)
        
        vpn_app_label = ttk.Label(
            vpn_app_frame,
            text="VPN application:",
            width=20
        )
        vpn_app_label.pack(side="left", padx=(0, 5))
        
        self.vpn_app_var = tk.StringVar(value="openvpn-gui.exe")
        vpn_app_entry = ttk.Entry(
            vpn_app_frame,
            textvariable=self.vpn_app_var,
            width=40
        )
        vpn_app_entry.pack(side="left", fill="x", expand=True)
        
        # VPN process name
        vpn_process_frame = ttk.Frame(self.vpn_options_frame)
        vpn_process_frame.pack(fill="x", pady=5)
        
        vpn_process_label = ttk.Label(
            vpn_process_frame,
            text="VPN process name:",
            width=20
        )
        vpn_process_label.pack(side="left", padx=(0, 5))
        
        self.vpn_process_var = tk.StringVar(value="openvpn")
        vpn_process_entry = ttk.Entry(
            vpn_process_frame,
            textvariable=self.vpn_process_var,
            width=40
        )
        vpn_process_entry.pack(side="left", fill="x", expand=True)
        
        # VPN config file
        vpn_config_frame = ttk.Frame(self.vpn_options_frame)
        vpn_config_frame.pack(fill="x", pady=5)
        
        vpn_config_label = ttk.Label(
            vpn_config_frame,
            text="VPN config file:",
            width=20
        )
        vpn_config_label.pack(side="left", padx=(0, 5))
        
        self.vpn_config_var = tk.StringVar(value="cash_me_outside_how_abou_dat.ovpn")
        vpn_config_entry = ttk.Entry(
            vpn_config_frame,
            textvariable=self.vpn_config_var,
            width=40
        )
        vpn_config_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_vpn_config_button = ttk.Button(
            vpn_config_frame,
            text="Browse...",
            command=self.browse_vpn_config
        )
        browse_vpn_config_button.pack(side="right")
        
        # Seconds to wait
        vpn_wait_frame = ttk.Frame(self.vpn_options_frame)
        vpn_wait_frame.pack(fill="x", pady=5)
        
        vpn_wait_label = ttk.Label(
            vpn_wait_frame,
            text="Seconds to wait:",
            width=20
        )
        vpn_wait_label.pack(side="left", padx=(0, 5))
        
        self.vpn_wait_var = tk.IntVar(value=10)
        vpn_wait_spinbox = ttk.Spinbox(
            vpn_wait_frame,
            from_=1,
            to=60,
            textvariable=self.vpn_wait_var,
            width=5
        )
        vpn_wait_spinbox.pack(side="left")
    
    def create_osd_section(self, parent):
        """Create the OSD configuration section."""
        osd_frame = ttk.LabelFrame(
            parent,
            text="On-Screen Display Configuration (Windows Only)",
            padding=(10, 5)
        )
        osd_frame.pack(fill="x", pady=10)
        
        # Enable OSD
        self.enable_osd_var = tk.BooleanVar(value=True)
        osd_text = "Kiosk mode on a Windows machine makes the native on-screen display for volume not usable. Would you like to enable a replacement OSD?"
        enable_osd = ttk.Checkbutton(
            osd_frame,
            text=osd_text,
            variable=self.enable_osd_var
        )
        enable_osd.pack(anchor="w", pady=5)
        
        # OSD information
        osd_info = ttk.Label(
            osd_frame,
            text="AudioSwitch will be installed to handle volume display. Settings will be configured automatically.",
            wraplength=500,
            foreground="gray"
        )
        osd_info.pack(anchor="w", padx=20, pady=5)
    
    def toggle_lights_options(self):
        """Show or hide lights options based on checkbox state."""
        if self.enable_lights_var.get():
            self.lights_options_frame.pack(fill="x", pady=5)
        else:
            self.lights_options_frame.pack_forget()
    
    def toggle_streaming_options(self):
        """Show or hide streaming options based on checkbox state."""
        if self.enable_streaming_var.get():
            self.streaming_options_frame.pack(fill="x", pady=5)
        else:
            self.streaming_options_frame.pack_forget()
    
    def toggle_webcam_options(self):
        """Show or hide webcam options based on checkbox state."""
        if self.enable_webcam_var.get():
            self.webcam_options_frame.pack(fill="x", pady=5)
        else:
            self.webcam_options_frame.pack_forget()
    
    def toggle_vpn_options(self):
        """Show or hide VPN options based on checkbox state."""
        if self.enable_vpn_var.get():
            self.vpn_options_frame.pack(fill="x", pady=5)
        else:
            self.vpn_options_frame.pack_forget()
    
    def browse_lights_reset(self):
        """Browse for the lights reset executable."""
        file_path = filedialog.askopenfilename(
            title="Select Lights Reset Executable",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        
        if file_path:
            self.lights_reset_var.set(file_path)
    
    def browse_lights_mame(self):
        """Browse for the lights MAME executable."""
        file_path = filedialog.askopenfilename(
            title="Select Lights MAME Executable",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        
        if file_path:
            self.lights_mame_var.set(file_path)
    
    def browse_webcam_exe(self):
        """Browse for the webcam management executable."""
        file_path = filedialog.askopenfilename(
            title="Select Webcam Management Application",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        
        if file_path:
            self.webcam_exe_var.set(file_path)
    
    def browse_obs_exe(self):
        """Browse for the OBS executable."""
        file_path = filedialog.askopenfilename(
            title="Select OBS Studio Executable",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        
        if file_path:
            self.obs_exe_var.set(file_path)
    
    def browse_vpn_dir(self):
        """Browse for the VPN installation directory."""
        dir_path = filedialog.askdirectory(
            title="Select VPN Installation Directory"
        )
        
        if dir_path:
            self.vpn_dir_var.set(dir_path)
    
    def browse_vpn_config(self):
        """Browse for the VPN configuration file."""
        file_path = filedialog.askopenfilename(
            title="Select VPN Configuration File",
            filetypes=[("OpenVPN files", "*.ovpn"), ("All files", "*.*")]
        )
        
        if file_path:
            self.vpn_config_var.set(os.path.basename(file_path))
    
    def validate(self):
        """Validate utility configuration."""
        if self.is_windows and self.enable_lights_var.get():
            # Validate light reset executable path
            if not self.lights_reset_var.get().strip():
                messagebox.showerror(
                    "Invalid Lights Reset Path", 
                    "Please specify a path for the lights reset executable."
                )
                return False
            
            # Validate light MAME executable path
            if not self.lights_mame_var.get().strip():
                messagebox.showerror(
                    "Invalid Lights MAME Path", 
                    "Please specify a path for the lights MAME executable."
                )
                return False
        
        if self.enable_streaming_var.get():
            # Validate webcam executable if enabled
            if self.enable_webcam_var.get() and not self.webcam_exe_var.get().strip():
                messagebox.showerror(
                    "Invalid Webcam Application", 
                    "Please specify a path for the webcam management application."
                )
                return False
            
            # Validate OBS executable
            if not self.obs_exe_var.get().strip():
                messagebox.showerror(
                    "Invalid OBS Path", 
                    "Please specify a path for the OBS Studio executable."
                )
                return False
        
        if self.is_windows and self.enable_vpn_var.get():
            # Validate VPN directory
            if not self.vpn_dir_var.get().strip():
                messagebox.showerror(
                    "Invalid VPN Directory", 
                    "Please specify the VPN installation directory."
                )
                return False
            
            # Validate VPN application
            if not self.vpn_app_var.get().strip():
                messagebox.showerror(
                    "Invalid VPN Application", 
                    "Please specify the VPN application filename."
                )
                return False
            
            # Validate VPN process
            if not self.vpn_process_var.get().strip():
                messagebox.showerror(
                    "Invalid VPN Process", 
                    "Please specify the VPN process name."
                )
                return False
            
            # Validate VPN config
            if not self.vpn_config_var.get().strip():
                messagebox.showerror(
                    "Invalid VPN Config", 
                    "Please specify the VPN configuration file."
                )
                return False
        
        return True
    
    def save_data(self):
        """Save utility configuration to the user config."""
        utilities_config = {}
        
        # Save lights configuration
        if self.is_windows:
            utilities_config["lights"] = {
                "enabled": self.enable_lights_var.get(),
                "light_reset_executable_path": self.lights_reset_var.get() if self.enable_lights_var.get() else "",
                "light_mame_executable_path": self.lights_mame_var.get() if self.enable_lights_var.get() else ""
            }
        
        # Save streaming configuration
        utilities_config["streaming"] = {
            "webcam_management_enabled": self.enable_webcam_var.get() if self.enable_streaming_var.get() else False,
            "webcam_management_executable": self.webcam_exe_var.get() if self.enable_streaming_var.get() and self.enable_webcam_var.get() else "",
            "obs_executable": self.obs_exe_var.get() if self.enable_streaming_var.get() else "",
            "obs_arguments": self.obs_args_var.get() if self.enable_streaming_var.get() else ""
        }
        
        # Save VPN configuration
        if self.is_windows:
            utilities_config["vpn"] = {
                "enabled": self.enable_vpn_var.get(),
                "vpn_application_directory": self.vpn_dir_var.get() if self.enable_vpn_var.get() else "",
                "vpn_application": self.vpn_app_var.get() if self.enable_vpn_var.get() else "",
                "vpn_process": self.vpn_process_var.get() if self.enable_vpn_var.get() else "",
                "vpn_config_profile": self.vpn_config_var.get() if self.enable_vpn_var.get() else "",
                "seconds_to_wait": self.vpn_wait_var.get()
            }
        
        # Save OSD configuration
        if self.is_windows:
            utilities_config["osd"] = {
                "enabled": self.enable_osd_var.get(),
                "sound_osd_executable": "../bin/windows/AudioSwitch/AudioSwitch.exe"
            }
        
        self.app.user_config["utilities"] = utilities_config
        
        # Initialize toggle states for the UI
        self.toggle_lights_options()
        self.toggle_streaming_options()
        self.toggle_webcam_options()
        self.toggle_vpn_options() 