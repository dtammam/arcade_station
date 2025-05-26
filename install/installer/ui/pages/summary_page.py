"""
Summary page for the Arcade Station Installer
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox
import json
import subprocess
import platform

from .base_page import BasePage

class SummaryPage(BasePage):
    """Summary page showing all configuration before installation."""
    
    def __init__(self, container, app):
        """Initialize the summary page."""
        super().__init__(container, app)
        self.set_title(
            "Installation Summary",
            "Review your configuration before installation"
        )
    
    def on_enter(self):
        """Called when the page is shown."""
        self.update_summary_text()
        
        # Update button text based on installation state
        if self.app.install_manager.files_copied:
            self.set_next_button_text("Finish")
        else:
            self.set_next_button_text("Install")
    
    def create_widgets(self):
        """Create page-specific widgets."""
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Introduction
        intro_text = ttk.Label(
            main_frame,
            text="Review your Arcade Station configuration before installation. "
                 "If you need to make changes, use the 'Previous' button to navigate back.",
            wraplength=500,
            justify="left"
        )
        intro_text.pack(anchor="w", pady=(0, 15))
        
        # Configuration summary frame
        summary_frame = ttk.LabelFrame(
            main_frame,
            text="Configuration Summary",
            padding=(10, 5)
        )
        summary_frame.pack(fill="both", expand=True, pady=10)
        
        # Create a frame with scrollbar for the summary
        canvas_frame = ttk.Frame(summary_frame)
        canvas_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.canvas = tk.Canvas(
            canvas_frame,
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            canvas_frame,
            orient="vertical",
            command=self.canvas.yview
        )
        
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Summary text
        self.summary_text = tk.Text(
            self.scrollable_frame,
            wrap="word",
            width=80,
            height=25,
            font=("Segoe UI", 10),
            padx=10,
            pady=10,
            state="disabled"
        )
        self.summary_text.pack(fill="both", expand=True)
        
        # Configure canvas to expand with window
        main_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(width=e.width - 50)
        )
        
        # Ready to install label
        ready_label = ttk.Label(
            main_frame,
            text="When you're ready to finalize the installation, select 'Finish'.",
            font=("Segoe UI", 10, "bold"),
            wraplength=500,
            justify="left"
        )
        ready_label.pack(anchor="w", pady=10)
    
    def update_summary_text(self):
        """Update the summary text with the current configuration."""
        # Enable editing
        self.summary_text.config(state="normal")
        
        # Clear any existing text
        self.summary_text.delete(1.0, "end")
        
        # Insert summary header
        self.summary_text.insert("end", "INSTALLATION SUMMARY\n", "header")
        self.summary_text.insert("end", "===================\n\n")
        
        # Installation path
        self.summary_text.insert("end", "Installation Path:\n", "section")
        self.summary_text.insert("end", f"{self.app.user_config.get('install_path', 'Not specified')}\n\n")
        
        # Installation status
        self.summary_text.insert("end", "Installation Status:\n", "section")
        if self.app.install_manager.files_copied:
            self.summary_text.insert("end", "Files have been copied to the installation location.\n")
            self.summary_text.insert("end", "Configuration files are being updated as you make changes.\n\n")
        else:
            self.summary_text.insert("end", "Files will be copied when you click 'Install'.\n\n")
        
        # Display configuration
        self.summary_text.insert("end", "Display Configuration:\n", "section")
        self.summary_text.insert("end", f"Dynamic Marquee: {'Enabled' if self.app.user_config.get('use_dynamic_marquee', False) else 'Disabled'}\n")
        
        if self.app.user_config.get('use_dynamic_marquee', False):
            self.summary_text.insert("end", f"Marquee Monitor: {self.app.user_config.get('marquee_monitor', 1)}\n")
            self.summary_text.insert("end", f"Background Color: {self.app.user_config.get('marquee_background_color', 'black')}\n")
            
            default_image = self.app.user_config.get('default_marquee_image', '')
            if default_image:
                self.summary_text.insert("end", f"Default Image: {default_image}\n")
            
            self.summary_text.insert("end", f"ITGMania Integration: {'Enabled' if self.app.user_config.get('enable_itgmania_display', False) else 'Disabled'}\n")
        
        self.summary_text.insert("end", "\n")
        
        # Game configuration
        self.summary_text.insert("end", "Game Configuration:\n", "section")
        
        # ITGMania
        itgmania_path = self.app.user_config.get('itgmania_path', '')
        if itgmania_path:
            self.summary_text.insert("end", f"ITGMania: {itgmania_path}\n")
        
        # Binary games
        binary_games = self.app.user_config.get('binary_games', {})
        if binary_games:
            self.summary_text.insert("end", "\nBinary Games:\n")
            for game_id, game_info in binary_games.items():
                self.summary_text.insert("end", f"- {game_info.get('display_name', game_id)}: {game_info.get('path', 'No path')}\n")
        
        # MAME games
        mame_games = self.app.user_config.get('mame_games', {})
        if mame_games:
            self.summary_text.insert("end", "\nMAME Games:\n")
            for game_id, game_info in mame_games.items():
                self.summary_text.insert("end", f"- {game_info.get('display_name', game_id)}: {game_info.get('rom', 'No ROM')}\n")
        
        self.summary_text.insert("end", "\n")
        
        # System configuration
        self.summary_text.insert("end", "System Configuration:\n", "section")
        
        # Kiosk mode
        kiosk_mode = self.app.user_config.get('enable_kiosk_mode', False)
        self.summary_text.insert("end", f"Kiosk Mode: {'Enabled' if kiosk_mode else 'Disabled'}\n")
        
        if kiosk_mode:
            self.summary_text.insert("end", f"Replace Shell: {'Yes' if self.app.user_config.get('kiosk_replace_shell', False) else 'No'}\n")
        
        # Key Bindings
        key_bindings = self.app.user_config.get('key_bindings', [])
        if key_bindings:
            self.summary_text.insert("end", "\nKey Bindings:\n")
            for binding in key_bindings:
                if binding.get('function') and binding.get('script_path') and binding.get('key'):
                    self.summary_text.insert("end", f"- {binding['function']}: {binding['key']} -> {binding['script_path']}\n")
        
        # Process Management
        process_management = self.app.user_config.get('process_management', {})
        if process_management:
            self.summary_text.insert("end", "\nProcess Management:\n")
            for process_name, process_info in process_management.items():
                self.summary_text.insert("end", f"- {process_name}: {process_info.get('path', 'No path')}\n")
        
        # Utility Configuration
        self.summary_text.insert("end", "\nUtility Configuration:\n", "section")
        
        utilities_config = self.app.user_config.get('utilities', {})
        
        # Lights Configuration
        lights_config = utilities_config.get('lights', {})
        if lights_config.get('enabled', False):
            self.summary_text.insert("end", "\nLights Configuration:\n")
            self.summary_text.insert("end", f"Lights Reset Program: {lights_config.get('light_reset_executable_path', 'Not specified')}\n")
            self.summary_text.insert("end", f"Lights MAME Executable: {lights_config.get('light_mame_executable_path', 'Not specified')}\n")
        
        # Streaming Configuration
        streaming_config = utilities_config.get('streaming', {})
        if streaming_config.get('obs_executable'):
            self.summary_text.insert("end", "\nStreaming Configuration:\n")
            self.summary_text.insert("end", f"OBS Executable: {streaming_config.get('obs_executable', 'Not specified')}\n")
            if streaming_config.get('obs_arguments'):
                self.summary_text.insert("end", f"OBS Arguments: {streaming_config.get('obs_arguments', 'Not specified')}\n")
            if streaming_config.get('webcam_management_enabled', False):
                self.summary_text.insert("end", f"Webcam Executable: {streaming_config.get('webcam_management_executable', 'Not specified')}\n")
        
        # VPN Configuration
        vpn_config = utilities_config.get('vpn', {})
        if vpn_config.get('enabled', False):
            self.summary_text.insert("end", "\nVPN Configuration:\n")
            self.summary_text.insert("end", f"VPN Directory: {vpn_config.get('vpn_application_directory', 'Not specified')}\n")
            self.summary_text.insert("end", f"VPN Application: {vpn_config.get('vpn_application', 'Not specified')}\n")
            self.summary_text.insert("end", f"VPN Process: {vpn_config.get('vpn_process', 'Not specified')}\n")
            self.summary_text.insert("end", f"VPN Config: {vpn_config.get('vpn_config_profile', 'Not specified')}\n")
            self.summary_text.insert("end", f"Wait Time: {vpn_config.get('seconds_to_wait', 'Not specified')} seconds\n")
        
        # OSD Configuration
        osd_config = utilities_config.get('osd', {})
        if osd_config.get('enabled', False):
            self.summary_text.insert("end", "\nOSD Configuration:\n")
            self.summary_text.insert("end", f"OSD Executable: {osd_config.get('sound_osd_executable', 'Not specified')}\n")
        
        # Screenshot Configuration
        screenshot_config = self.app.user_config.get('screenshot', {})
        if screenshot_config.get('enabled', False):
            self.summary_text.insert("end", "\nScreenshot Configuration:\n")
            self.summary_text.insert("end", f"Screenshot Location: {screenshot_config.get('file_location', 'Not specified')}\n")
            self.summary_text.insert("end", f"Monitor Index: {screenshot_config.get('monitor_index', 'Not specified')}\n")
            self.summary_text.insert("end", f"Sound File: {screenshot_config.get('sound_file', 'Not specified')}\n")
        
        # Style the text
        self.summary_text.tag_configure("header", font=("Segoe UI", 12, "bold"))
        self.summary_text.tag_configure("section", font=("Segoe UI", 10, "bold"))
        
        # Disable editing
        self.summary_text.config(state="disabled")
    
    def on_next(self):
        """Handle the next button click."""
        if not self.app.install_manager.files_copied:
            # If files haven't been copied yet, install now
            self.install()
        else:
            # Files already copied, just finish
            message = "Arcade Station has been successfully installed and configured!\n\nYou can now start using it."
            if platform.system().lower() == "windows":
                message += "\nPlease launch `launch_arcade_station.bat` to accept the security prompt before switching to kiosk mode."
            
            messagebox.showinfo("Installation Complete", message)
            
            # Open the installation directory after the message box is closed
            install_path = self.app.user_config.get('install_path')
            if install_path and os.path.exists(install_path):
                if platform.system().lower() == "windows":
                    os.startfile(install_path)
                elif platform.system().lower() == "darwin":  # macOS
                    subprocess.run(["open", install_path])
                else:  # Linux
                    subprocess.run(["xdg-open", install_path])
            super().on_next()
    
    def install(self):
        """Perform the installation."""
        # Show a progress dialog
        progress_window = tk.Toplevel(self.app.root)
        progress_window.title("Installing Arcade Station")
        progress_window.geometry("400x150")
        progress_window.transient(self.app.root)
        progress_window.grab_set()
        
        # Center the window
        progress_window.update_idletasks()
        width = progress_window.winfo_width()
        height = progress_window.winfo_height()
        x = (progress_window.winfo_screenwidth() // 2) - (width // 2)
        y = (progress_window.winfo_screenheight() // 2) - (height // 2)
        progress_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Add a header
        header_label = ttk.Label(
            progress_window,
            text="Installing Arcade Station",
            font=("Segoe UI", 12, "bold")
        )
        header_label.pack(pady=(10, 5))
        
        # Status label
        status_label = ttk.Label(
            progress_window,
            text="Please wait while the installation is completed...",
            wraplength=380,
            justify="center"
        )
        status_label.pack(pady=5)
        
        # Progress bar
        progress_bar = ttk.Progressbar(
            progress_window,
            mode="indeterminate"
        )
        progress_bar.pack(fill="x", padx=20, pady=10)
        progress_bar.start()
        
        # Update the UI
        progress_window.update()
        
        # Perform the installation in a separate thread to keep the UI responsive
        import threading
        
        def install_thread():
            success = self.app.install_manager.perform_installation(self.app.user_config)
            
            # Update the UI on the main thread
            self.app.root.after(0, lambda: self.installation_complete(success, progress_window))
        
        threading.Thread(target=install_thread).start()
    
    def installation_complete(self, success, progress_window):
        """Handle installation completion.
        
        Args:
            success: Whether the installation was successful
            progress_window: The progress dialog to close
        """
        # Close the progress window
        progress_window.destroy()
        
        if success:
            messagebox.showinfo(
                "Installation Complete",
                "Arcade Station has been successfully installed!\n\n"
                "You can now start using it."
            )
            # Open the installation directory after the message box is closed
            install_path = self.app.user_config.get('install_path')
            if install_path and os.path.exists(install_path):
                if platform.system().lower() == "windows":
                    os.startfile(install_path)
                elif platform.system().lower() == "darwin":  # macOS
                    subprocess.run(["open", install_path])
                else:  # Linux
                    subprocess.run(["xdg-open", install_path])
            super().on_next()
        else:
            messagebox.showerror(
                "Installation Failed",
                "The installation could not be completed. Please check the logs for details."
            )
    
    def export_config(self):
        """Export the configuration to a JSON file."""
        save_path = tk.filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Configuration"
        )
        
        if not save_path:
            return
        
        try:
            with open(save_path, 'w') as f:
                json.dump(self.app.user_config, f, indent=4)
            
            messagebox.showinfo(
                "Export Successful",
                f"Configuration exported to {save_path}"
            )
        except Exception as e:
            messagebox.showerror(
                "Export Failed",
                f"Failed to export configuration: {str(e)}"
            )
    
    def validate(self):
        """Validate the page."""
        # Nothing to validate on the summary page
        return True
    
    def save_data(self):
        """Save data from the page."""
        # Nothing to save on the summary page
        pass 