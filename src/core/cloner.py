import os
from git import Repo

class RepositoryCloner:
    def __init__(self, repo_url, clone_dir):
        self.repo_url = repo_url
        self.clone_dir = clone_dir

    def clone_repository(self):
        if os.path.exists(self.clone_dir):
            print(f"Directory '{self.clone_dir}' already exists. Skipping cloning.")
            return
        try:
            print(f"Cloning repository from {self.repo_url} to {self.clone_dir}...")
            Repo.clone_from(self.repo_url, self.clone_dir)
            print("Repository cloned successfully.")
        except Exception as e:
            print(f"Error cloning repository: {e}")

    