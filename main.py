import os
import tarfile
import json
import threading
import logging
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window

# Configure logging
logging.basicConfig(filename='log_archiver_errors.log', level=logging.ERROR)

# Default log directories
DEFAULT_LOG_DIRECTORIES = [
    "/var/log",
    "/home",
    "/tmp",
    "/var/tmp",
    "/etc",
]

class LogArchiverApp(App):
    """
    Main application class for the log archiver tool.
    """

    def build(self):
        Window.clearcolor = (0.95, 0.95, 0.95, 1)  # Light background color
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Title
        title_label = Label(text="Log Archiver Tool", font_size='24sp', size_hint_y=None, height=50)
        layout.add_widget(title_label)

        # User management
        self.username_input = TextInput(hint_text="Username", size_hint=(1, 0.1), background_color=(1, 1, 1, 1))
        layout.add_widget(self.username_input)
        self.password_input = TextInput(hint_text="Password", password=True, size_hint=(1, 0.1), background_color=(1, 1, 1, 1))
        layout.add_widget(self.password_input)

        login_button = Button(text="Login", size_hint=(1, 0.1), background_color=(0.8, 0.8, 0.8, 1))
        login_button.bind(on_press=self.login)
        layout.add_widget(login_button)

        register_button = Button(text="Register", size_hint=(1, 0.1), background_color=(0.8, 0.8, 0.8, 1))
        register_button.bind(on_press=self.register)
        layout.add_widget(register_button)

        # Info label
        self.info_label = Label(text="Select a location to save the log archive", size_hint=(1, 0.1))
        layout.add_widget(self.info_label)

        # File chooser for selecting save location
        self.file_chooser = FileChooserIconView()
        layout.add_widget(self.file_chooser)

        # Progress bar
        self.progress_bar = ProgressBar(max=100, size_hint=(1, 0.1))  # No color attribute here
        layout.add_widget(self.progress_bar)

        # Archive button
        archive_button = Button(text="Archive Logs", size_hint=(1, 0.1), background_color=(0.8, 0.8, 0.8, 1))
        archive_button.bind(on_press=self.archive_logs)
        layout.add_widget(archive_button)

        # Clean button
        clean_button = Button(text="Clean Old Logs", size_hint=(1, 0.1), background_color=(0.8, 0.8, 0.8, 1))
        clean_button.bind(on_press=self.clean_logs)
        layout.add_widget(clean_button)

        # Custom log directory management
        self.custom_log_layout = GridLayout(cols=1, size_hint_y=None)
        self.custom_log_layout.bind(minimum_height=self.custom_log_layout.setter('height'))

        self.log_list_scroll = ScrollView(size_hint=(1, 0.3))
        self.log_list_scroll.add_widget(self.custom_log_layout)
        layout.add_widget(self.log_list_scroll)

        add_log_dir_button = Button(text="Add Log Directory", size_hint=(1, 0.1), background_color=(0.8, 0.8, 0.8, 1))
        add_log_dir_button.bind(on_press=self.add_log_directory)
        layout.add_widget(add_log_dir_button)

        self.load_settings()

        return layout

    def load_settings(self):
        """
        Loads log directory settings from a JSON file.
        """
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                global DEFAULT_LOG_DIRECTORIES
                DEFAULT_LOG_DIRECTORIES = settings.get('log_directories', DEFAULT_LOG_DIRECTORIES)
                self.update_log_directory_list()
                self.show_popup("Settings Loaded", "Log directories have been updated.")
        except FileNotFoundError:
            self.show_popup("Error", "Settings file not found. Using default directories.")
        except Exception as e:
            self.show_popup("Error", f"Failed to load settings: {str(e)}")

    def update_log_directory_list(self):
        """
        Updates the displayed list of custom log directories.
        """
        self.custom_log_layout.clear_widgets()
        for directory in DEFAULT_LOG_DIRECTORIES:
            label = Label(text=directory, size_hint_y=None, height=40)
            remove_button = Button(text="Remove", size_hint_y=None, height=40, background_color=(0.8, 0.8, 0.8, 1))
            remove_button.bind(on_press=lambda instance, dir=directory: self.remove_log_directory(dir))
            self.custom_log_layout.add_widget(label)
            self.custom_log_layout.add_widget(remove_button)

    def remove_log_directory(self, directory):
        """
        Removes a log directory from the custom log directory list.
        """
        global DEFAULT_LOG_DIRECTORIES
        DEFAULT_LOG_DIRECTORIES.remove(directory)
        self.update_log_directory_list()
        self.save_settings()

    def add_log_directory(self, instance):
        """
        Prompts the user to add a new log directory.
        """
        self.show_input_popup("Add Log Directory", "Enter the new log directory path:", self.add_directory_callback)

    def add_directory_callback(self, directory):
        """
        Callback for adding a new directory.
        """
        if directory and os.path.isdir(directory):
            global DEFAULT_LOG_DIRECTORIES
            DEFAULT_LOG_DIRECTORIES.append(directory)
            self.update_log_directory_list()
            self.save_settings()
        else:
            self.show_popup("Error", "Invalid directory path.")

    def show_input_popup(self, title, message, callback):
        """
        Displays a popup with an input field for user input.

        :param title: Title of the popup.
        :param message: Message to display.
        :param callback: Callback function to handle the input.
        """
        layout = BoxLayout(orientation='vertical', padding=10)
        input_field = TextInput(hint_text=message, background_color=(1, 1, 1, 1))
        layout.add_widget(input_field)
        submit_button = Button(text="Submit", background_color=(0.8, 0.8, 0.8, 1))
        layout.add_widget(submit_button)

        popup = Popup(title=title, content=layout, size_hint=(0.8, 0.4))
        submit_button.bind(on_press=lambda x: [callback(input_field.text), popup.dismiss()])
        popup.open()

    def login(self, instance):
        """
        Simple user authentication for accessing the app features.
        """
        username = self.username_input.text
        password = self.password_input.text

        # For demonstration purposes, use hardcoded credentials
        if username == "admin" and password == "password":
            self.show_popup("Login Successful!", "Welcome to the Log Archiver Tool.")
        else:
            self.show_popup("Login Failed", "Invalid username or password.")

    def register(self, instance):
        """
        Simple user registration (for demonstration purposes).
        """
        username = self.username_input.text
        password = self.password_input.text

        # In a real application, you would want to save the user credentials securely
        self.show_popup("Registration Successful", f"User '{username}' registered successfully!")

    def archive_logs(self, instance):
        """
        Archives logs from specified directories to a chosen location.
        """
        save_path = self.file_chooser.selection[0] if self.file_chooser.selection else None
        if save_path:
            date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            archive_name = os.path.join(save_path, f"log_archive_{date_str}.tar.gz")
            self.progress_bar.value = 0

            threading.Thread(target=self.create_archive, args=(DEFAULT_LOG_DIRECTORIES, archive_name)).start()
        else:
            self.show_popup("Error", "Please select a directory to save the archive.")

    def create_archive(self, log_dirs, archive_path):
        """
        Creates a tar.gz archive of log files.

        :param log_dirs: List of directories to archive.
        :param archive_path: Path to save the archive.
        """
        try:
            with tarfile.open(archive_path, "w:gz") as tar:
                total_files = sum(len(files) for log_dir in log_dirs for _, _, files in os.walk(log_dir))
                processed_files = 0

                for log_dir in log_dirs:
                    for root, dirs, files in os.walk(log_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            tar.add(file_path, arcname=os.path.relpath(file_path, log_dir))
                            processed_files += 1
                            self.progress_bar.value = (processed_files / total_files) * 100

            self.show_popup("Success", "Log archive created successfully!")
        except Exception as e:
            logging.error(f"Error creating archive: {str(e)}")
            self.show_popup("Error", f"Failed to create log archive: {str(e)}")

    def clean_logs(self, instance):
        """
        Cleans old log files from specified directories.
        """
        for log_dir in DEFAULT_LOG_DIRECTORIES:
            try:
                for root, dirs, files in os.walk(log_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if self.should_delete(file_path):
                            os.remove(file_path)
                            logging.info(f"Deleted log file: {file_path}")
                self.show_popup("Success", "Old logs cleaned successfully!")
            except Exception as e:
                logging.error(f"Error cleaning logs: {str(e)}")
                self.show_popup("Error", f"Failed to clean logs: {str(e)}")

    def should_delete(self, file_path):
        """
        Determines if a log file should be deleted based on specific criteria.
        """
        # Implement your own logic to decide if a file should be deleted
        return True

    def save_settings(self):
        """
        Saves log directory settings to a JSON file.
        """
        try:
            with open('settings.json', 'w') as f:
                json.dump({'log_directories': DEFAULT_LOG_DIRECTORIES}, f)
        except Exception as e:
            logging.error(f"Error saving settings: {str(e)}")

    def show_popup(self, title, message):
        """
        Displays a simple popup with a message.

        :param title: Title of the popup.
        :param message: Message to display.
        """
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.4))
        popup.open()


if __name__ == "__main__":
    LogArchiverApp().run()
