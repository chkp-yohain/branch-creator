import sys
import os
import git
import re
from multiprocessing import freeze_support

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, 
    QComboBox, QLineEdit, QFileDialog, QMessageBox, QTabWidget, QFormLayout
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

if __name__ == '__main__':
    freeze_support()
    
    # Add a small startup delay to allow macOS to properly initialize the app
    import time
    time.sleep(0.1)  # 100ms delay helps macOS process initialization better


class GitBranchManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Git Branch Manager")
        self.setGeometry(100, 100, 500, 400)
        self.initUI()

    def initUI(self):
        self.tabs = QTabWidget()
        self.main_tab = QWidget()
        self.settings_tab = QWidget()

        self.tabs.addTab(self.main_tab, "Main")
        
        self.initMainTab()

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Scan", os.path.expanduser("~"))
        if folder:
            self.folder_label.setText(f"Selected Folder: {folder}")
            self.load_git_repositories(folder)

    def initMainTab(self):
        layout = QVBoxLayout()

        # Folder Selection
        self.folder_label = QLabel("Selected Folder: None")
        self.select_folder_btn = QPushButton("Select Base Folder")
        self.select_folder_btn.clicked.connect(self.select_folder)

        # Repo Dropdown
        self.repo_combo = QComboBox()
        self.repo_combo.currentTextChanged.connect(self.on_repo_selected)

        layout.addWidget(self.folder_label)
        layout.addWidget(self.select_folder_btn)

        self.repo_label = QLabel("Select Repository:")
        layout.addWidget(self.repo_label)

        layout.addWidget(self.repo_combo)

        self.base_branch_label = QLabel("Select Base Branch:")
        layout.addWidget(self.base_branch_label)

        self.base_branch_combo = QComboBox()
        layout.addWidget(self.base_branch_combo)

        self.type_label = QLabel("Branch Type:")
        layout.addWidget(self.type_label)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["feature", "bugfix"])
        layout.addWidget(self.type_combo)

        self.ticket_label = QLabel("Jira Ticket: (e.g ABC-123)")
        layout.addWidget(self.ticket_label)

        self.ticket_combo = QLineEdit()
        layout.addWidget(self.ticket_combo)

        self.description_label = QLabel("Branch Description:")
        layout.addWidget(self.description_label)

        self.description_input = QLineEdit()
        layout.addWidget(self.description_input)

        self.create_button = QPushButton("Create Branch")
        self.create_button.clicked.connect(self.create_branch)
        layout.addWidget(self.create_button)

        self.main_tab.setLayout(layout)

    def load_git_repositories(self, folder):
        """Recursively scan the folder for Git repositories."""
        self.repo_combo.clear()
        
        repos = []
        for root, dirs, files in os.walk(folder):
            if '.git' in dirs:
                repos.append(root)
        
        if repos:
            self.repo_combo.addItems(repos)
        else:
            QMessageBox.warning(self, "No Repositories", "No Git repositories found in the selected folder.")

    def on_repo_selected(self):
        """Load the branches of the selected repo."""
        repo_path = self.repo_combo.currentText()
        if repo_path:
            self.load_branches(repo_path)

    def load_branches(self, repo_path):
        """Load the branches of the selected repo into the branch combo, excluding specific prefixes."""
        try:
            repo = git.Repo(repo_path)
            self.base_branch_combo.clear()

            # Fetch all branches and filter out those starting with feature/, feat/, bug/, or bugfix/
            branches = [branch.name for branch in repo.branches if not branch.name.startswith(('feature/', 'feat/', 'bug/', 'bugfix/'))]
            
            # Add the remaining branches to the combo
            self.base_branch_combo.addItems(branches)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load branches: {e}")

    def create_branch(self):
        repo_path = self.repo_combo.currentText()
        branch_type = self.type_combo.currentText()
        ticket_key = self.ticket_combo.text().strip()
        description = self.description_input.text().strip().replace(" ", "-")
        
        # Validate Jira ticket name with regex
        if not re.match(r"^[A-Za-z]+-\d+$", ticket_key):
            QMessageBox.warning(self, "Error", "Jira ticket name must follow the pattern *-*, e.g. ABC-123.")
            return

        base_branch = self.base_branch_combo.currentText()
        if not repo_path or not ticket_key or not description or not base_branch:
            QMessageBox.warning(self, "Error", "All fields are required.")
            return

        try:
            repo = git.Repo(repo_path)
            branch_name = f"{branch_type}/{ticket_key}/{base_branch}/{description}"
            repo.git.checkout(base_branch)  # Checkout the selected base branch
            repo.git.checkout('-b', branch_name)  # Create and switch to the new branch
            QMessageBox.information(self, "Success", f"Branch {branch_name} created and switched.")
        except Exception as e:
            QMessageBox.critical(self, "Git Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GitBranchManager()
    window.show()
    sys.exit(app.exec())
