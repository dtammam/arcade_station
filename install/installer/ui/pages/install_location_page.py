"""
Installation location page for the Arcade Station Installer
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from .base_page import BasePage

class InstallLocationPage(BasePage):
    """Page for selecting installation location."""
    
    def __init__(self, container, app):
        """Initialize the installation location page."""
        super().__init__(container, app)
        self.set_title(
            "Installation Location",
            "Choose where to install Arcade Station"
        )
    
    def create_widgets(self):
        """Create page-specific widgets."""
        location_frame = ttk.Frame(self.content_frame)
        location_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Instructions
        instruction_label = ttk.Label(
            location_frame,
            text="Select a directory where you want to install Arcade Station. "
                 "This is where all the necessary files will be stored.",
            wraplength=500,
            justify="left"
        )
        instruction_label.pack(anchor="w", pady=(0, 20))
        
        # Default location info
        if self.app.is_installed and self.app.is_reset_mode:
            # If in reset mode, show current installation path
            default_path = self.app.install_manager.get_current_install_path()
            message = "Current installation directory:"
        else:
            # For new installations, suggest a default path
            default_path = self.app.install_manager.get_suggested_install_path()
            message = "Suggested installation directory:"
        
        default_label = ttk.Label(
            location_frame,
            text=message,
            wraplength=500,
            justify="left"
        )
        default_label.pack(anchor="w", pady=(0, 5))
        
        # Path entry
        path_frame = ttk.Frame(location_frame)
        path_frame.pack(fill="x", pady=5)
        
        self.path_var = tk.StringVar(value=default_path)
        
        path_entry = ttk.Entry(
            path_frame,
            textvariable=self.path_var,
            width=50
        )
        path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_button = ttk.Button(
            path_frame,
            text="Browse...",
            command=self.browse_location
        )
        browse_button.pack(side="right")
        
        # Space requirements
        requirements_frame = ttk.LabelFrame(
            location_frame,
            text="Requirements",
            padding=(10, 5)
        )
        requirements_frame.pack(fill="x", pady=20)
        
        space_label = ttk.Label(
            requirements_frame,
            text="Disk space required: Approximately 500 MB (excluding games)",
            wraplength=500,
            justify="left"
        )
        space_label.pack(anchor="w", pady=5)
        
        permission_label = ttk.Label(
            requirements_frame,
            text="You must have write permissions to the selected directory.",
            wraplength=500,
            justify="left"
        )
        permission_label.pack(anchor="w", pady=5)
        
        # Warning about existing installation
        if self.app.is_installed and not self.app.is_reset_mode:
            warning_frame = ttk.Frame(location_frame)
            warning_frame.pack(fill="x", pady=10)
            
            warning_label = ttk.Label(
                warning_frame,
                text="Warning: A new installation will not remove the existing installation. "
                     "To avoid conflicts, consider using the same location as the existing installation "
                     "or completely removing the old installation first.",
                wraplength=500,
                foreground="red",
                justify="left"
            )
            warning_label.pack(anchor="w")
    
    def browse_location(self):
        """Open a directory browser dialog."""
        current_path = self.path_var.get()
        initial_dir = current_path if os.path.isdir(current_path) else os.path.expanduser("~")
        
        selected_dir = filedialog.askdirectory(
            title="Select Installation Directory",
            initialdir=initial_dir
        )
        
        if selected_dir:
            self.path_var.set(selected_dir)
    
    def validate(self):
        """Validate the installation path."""
        path = self.path_var.get().strip()
        
        if not path:
            messagebox.showerror(
                "Invalid Path", 
                "Please enter a valid installation path."
            )
            return False
        
        # Check if path exists and can be written to
        if not os.path.isdir(path):
            try:
                os.makedirs(path, exist_ok=True)
            except Exception as e:
                messagebox.showerror(
                    "Permission Error", 
                    f"Cannot create directory: {e}"
                )
                return False
        
        # Check write permissions by trying to create a test file
        test_file = os.path.join(path, ".arcade_station_test")
        try:
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
        except Exception as e:
            messagebox.showerror(
                "Permission Error", 
                f"Cannot write to the selected directory: {e}"
            )
            return False
        
        # Pre-check if Arcade Station is installed here
        self.app.user_config["install_path"] = path
        is_installed = self.app.check_installation_status()
        
        if is_installed:
            # Show options dialog
            result = messagebox.askyesnocancel(
                "Installation Detected",
                f"Arcade Station is already installed at:\n{path}\n\n"
                "Would you like to reconfigure the existing installation?\n\n"
                "Yes: Reconfigure existing installation\n"
                "No: Reset and reinstall at this location\n"
                "Cancel: Choose a different location"
            )
            
            if result is None:  # Cancel was pressed
                return False
            
            # Set appropriate installation mode
            if result:  # Yes was pressed
                self.app.is_reconfigure_mode = True
                self.app.install_manager.files_copied = True
            else:  # No was pressed - attempt to delete existing installation
                try:
                    # First try to delete everything except .git
                    for item in os.listdir(path):
                        item_path = os.path.join(path, item)
                        if item != '.git':
                            try:
                                if os.path.isfile(item_path):
                                    os.remove(item_path)
                                elif os.path.isdir(item_path):
                                    shutil.rmtree(item_path)
                            except Exception as e:
                                messagebox.showerror(
                                    "Delete Error",
                                    f"Could not delete {item}. Please close any programs using files in this directory and try again.\n\nError: {e}"
                                )
                                return False
                    
                    # Then try to delete .git if it exists
                    git_path = os.path.join(path, '.git')
                    if os.path.exists(git_path):
                        try:
                            shutil.rmtree(git_path)
                        except Exception:
                            # If we can't delete .git, just log it and continue
                            print("Warning: Could not delete .git directory, continuing with installation")
                    
                    # Recreate the directory
                    os.makedirs(path)
                    self.app.is_reset_mode = True
                    self.app.install_manager.files_copied = False
                except Exception as e:
                    messagebox.showerror(
                        "Reset Error",
                        f"An unexpected error occurred while resetting the installation: {e}"
                    )
                    return False
            
            # Update page flow based on the selected mode
            self.app.decide_next_page_flow()
            
            # Hide current page and refresh the UI to prevent splitting
            current_page_index = self.app.current_page
            for page in self.app.pages:
                page.hide()
            self.app.show_page(current_page_index)
        
        return True
    
    def save_data(self):
        """Save the installation path."""
        install_path = self.path_var.get().strip()
        self.app.user_config["install_path"] = install_path
        
        # Skip file copy if we're in reconfigure mode or files are already copied
        if self.app.is_reconfigure_mode or self.app.install_manager.files_copied:
            return
        
        # Immediately copy project files to the installation location
        progress_window = None
        try:
            # Show a progress indicator
            progress_window = tk.Toplevel(self.app.root)
            progress_window.title("Copying Files")
            progress_window.geometry("400x200")
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
                text="Copying Project Files",
                font=("Arial", 12, "bold")
            )
            header_label.pack(pady=(10, 5))
            
            # Add a description
            progress_label = ttk.Label(
                progress_window, 
                text=f"Copying files to:\n{install_path}",
                wraplength=380,
                justify="center"
            )
            progress_label.pack(pady=5)
            
            # Add a status label that will be updated
            status_label = ttk.Label(
                progress_window,
                text="Preparing...",
                wraplength=380,
                justify="center"
            )
            status_label.pack(pady=5)
            
            # Add progress bar
            progress_bar = ttk.Progressbar(
                progress_window,
                mode="indeterminate"
            )
            progress_bar.pack(fill="x", padx=20, pady=10)
            progress_bar.start()
            
            # Update the UI
            progress_window.update()
            
            # Define a callback to update the status label
            def update_status(message):
                status_label.config(text=message)
                progress_window.update()
            
            # Create the base directories
            update_status("Creating directory structure...")
            os.makedirs(install_path, exist_ok=True)
            src_dir = os.path.join(install_path, "src")
            os.makedirs(src_dir, exist_ok=True)
            config_dir = os.path.join(install_path, "config")
            os.makedirs(config_dir, exist_ok=True)
            
            # Patch the copy_project_files method to use our status callback
            original_copy = self.app.install_manager._copy_project_files
            
            def patched_copy(install_path):
                try:
                    import shutil
                    from pathlib import Path
                    import os
                    
                    # Get the current directory (where the installer is running from)
                    current_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
                    
                    # Show source directory in status
                    update_status(f"Copying from: {current_dir}")
                    
                    # Need to copy everything (all directories and files)
                    update_status("Starting full copy of all project files...")
                    
                    # Get all items in the current directory
                    all_items = list(current_dir.iterdir())
                    
                    # Keep a count for user feedback
                    total_dirs_copied = 0
                    total_files_copied = 0
                    
                    # Copy each item (except the installer while it's running)
                    for item in all_items:
                        # Skip the installer for now to avoid copying it while it's running
                        if item.name == "installer":
                            continue
                            
                        dst_path = Path(install_path) / item.name
                        
                        update_status(f"Copying {item.name}...")
                        
                        # Remove destination if it exists
                        if dst_path.exists():
                            if dst_path.is_dir():
                                shutil.rmtree(dst_path)
                            else:
                                os.remove(dst_path)
                        
                        # Copy directory or file with detailed status updates
                        if item.is_dir():
                            # Add a callback function to count items being copied
                            def copy_with_progress(src, dst):
                                nonlocal total_dirs_copied, total_files_copied
                                if os.path.isdir(src):
                                    total_dirs_copied += 1
                                    os.makedirs(dst, exist_ok=True)
                                    update_status(f"Copying directory: {os.path.basename(src)}")
                                    items = os.listdir(src)
                                    for item in items:
                                        s = os.path.join(src, item)
                                        d = os.path.join(dst, item)
                                        copy_with_progress(s, d)
                                else:
                                    total_files_copied += 1
                                    shutil.copy2(src, dst)
                            
                            # Use our custom recursive copy function
                            copy_with_progress(str(item), str(dst_path))
                        else:
                            shutil.copy2(item, dst_path)
                            total_files_copied += 1
                    
                    # Now copy the installer directory (without locking it up)
                    installer_src = current_dir / "installer"
                    installer_dst = Path(install_path) / "installer"
                    
                    if installer_src.exists():
                        update_status("Copying installer files...")
                        
                        # Create the destination directory
                        os.makedirs(installer_dst, exist_ok=True)
                        
                        # Copy all files and subdirectories in the installer except for any running processes
                        for item in installer_src.iterdir():
                            dst_item = installer_dst / item.name
                            try:
                                if item.is_dir():
                                    # Use our custom recursive copy function for complete copy
                                    def copy_installer_dir(src, dst):
                                        nonlocal total_dirs_copied, total_files_copied
                                        os.makedirs(dst, exist_ok=True)
                                        total_dirs_copied += 1
                                        
                                        for item in os.listdir(src):
                                            s = os.path.join(src, item)
                                            d = os.path.join(dst, item)
                                            
                                            if os.path.isdir(s):
                                                copy_installer_dir(s, d)
                                            else:
                                                try:
                                                    shutil.copy2(s, d)
                                                    total_files_copied += 1
                                                except (PermissionError, OSError) as e:
                                                    update_status(f"Skipping locked file: {os.path.basename(s)}")
                                    
                                    copy_installer_dir(str(item), str(dst_item))
                                else:
                                    try:
                                        shutil.copy2(item, dst_item)
                                        total_files_copied += 1
                                    except (PermissionError, OSError):
                                        update_status(f"Skipping locked file: {item.name}")
                            except Exception as e:
                                update_status(f"Error copying {item.name}: {str(e)}")
                    
                    # Ensure these specific directories exist even if not in source
                    required_dirs = [
                        "src/arcade_station",
                        "src/pegasus-fe/config/metafiles",
                        "config",
                        "assets/images/banners",
                        ".venv"
                    ]
                    
                    for dir_path in required_dirs:
                        dir_full_path = Path(install_path) / dir_path
                        if not dir_full_path.exists():
                            update_status(f"Creating required directory: {dir_path}")
                            os.makedirs(dir_full_path, exist_ok=True)
                    
                    # Mark files as copied
                    self.app.install_manager.files_copied = True
                    update_status(f"Copy completed: {total_dirs_copied} directories and {total_files_copied} files copied successfully!")
                    
                except Exception as e:
                    update_status(f"Error copying files: {str(e)}")
                    raise
            
            # Replace the method temporarily
            self.app.install_manager._copy_project_files = patched_copy
            
            try:
                # Copy the project files using our patched method
                self.app.install_manager._copy_project_files(install_path)
                
                # Wait a moment so the user can see the "success" message
                self.app.root.after(1000, lambda: progress_bar.stop())
                self.app.root.after(1500, lambda: progress_window.destroy())
                
                # Ensure we update the page flow to continue configuration
                # This is important to prevent the installer from prematurely finishing
                self.app.decide_next_page_flow()
                
            finally:
                # Restore the original method
                self.app.install_manager._copy_project_files = original_copy
            
        except Exception as e:
            # Set files_copied to False in case of error
            self.app.install_manager.files_copied = False
            
            # Clean up the progress window if it exists
            if progress_window and progress_window.winfo_exists():
                progress_window.destroy()
            
            # Show error and return to previous page
            messagebox.showerror(
                "Copy Error",
                f"An error occurred while copying files: {str(e)}\n\nPlease ensure you have sufficient permissions and try again."
            )
            
            # Go back to the previous page
            self.app.prev_page()
            return