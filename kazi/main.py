import os
import json
import argparse
from datetime import datetime

class Kazi:
    def __init__(self, repo_path=None, project_name=None):
        self.repo_path = repo_path or os.getcwd()
        self.kazi_dir = None
        if project_name:
            self.kazi_dir = os.path.join(self.repo_path, f".{project_name}")
        self.staging_file = os.path.join(self.kazi_dir, 'staging.json') if self.kazi_dir else None
        self.commits_file = os.path.join(self.kazi_dir, 'commits.json') if self.kazi_dir else None
        self.branches_file = os.path.join(self.kazi_dir, 'branches.json') if self.kazi_dir else None

    def kazi_init(self, project_name):
        """Initialize a repository."""
        self.kazi_dir = os.path.join(self.repo_path, f".{project_name}")
        print(f"Initializing repository at: {self.kazi_dir}")  # Debugging line
        self.staging_file = os.path.join(self.kazi_dir, 'staging.json')
        self.commits_file = os.path.join(self.kazi_dir, 'commits.json')
        self.branches_file = os.path.join(self.kazi_dir, 'branches.json')

        if os.path.exists(self.kazi_dir):
            print(f"Repository '{project_name}' already initialized.")
            return

        os.makedirs(self.kazi_dir)
        with open(self.staging_file, 'w') as f:
            json.dump([], f)
        with open(self.commits_file, 'w') as f:
            json.dump([], f)
        with open(self.branches_file, 'w') as f:
            json.dump({'main': {'commits': [], 'active': True}}, f)

        print(f"Initialized empty repository '{project_name}' at {self.kazi_dir}")

    def kazi_add(self, file_path):
        """Add a file to the staging area."""
        if not self.kazi_dir or not os.path.exists(self.kazi_dir):
            print("Not a repository. Run 'kazi init' first.")
            return

        if not os.path.exists(file_path):
            print(f"File '{file_path}' does not exist.")
            return

        print(f"Adding file: {file_path} to staging area.")  # Debugging line
        with open(self.staging_file, 'r+') as f:
            staged_files = json.load(f)
            if file_path not in staged_files:
                staged_files.append(file_path)
                f.seek(0)
                json.dump(staged_files, f, indent=2)
                print(f"Added '{file_path}' to staging area.")

    def kazi_commit(self, message):
        """Commit staged files with a message."""
        if not os.path.exists(self.kazi_dir):
            print("Not a repository. Run 'kazi init' first.")
            return

        with open(self.staging_file, 'r+') as sf, open(self.commits_file, 'r+') as cf, open(self.branches_file, 'r+') as bf:
            staged_files = json.load(sf)
            commits = json.load(cf)
            branches = json.load(bf)

            if not staged_files:
                print("No files to commit.")
                return

            commit_id = len(commits) + 1
            commit = {
                'id': commit_id,
                'message': message,
                'files': staged_files,
                'timestamp': datetime.now().isoformat()
            }

            commits.append(commit)
            active_branch = next(branch for branch, data in branches.items() if data['active'])
            branches[active_branch]['commits'].append(commit_id)

            sf.seek(0)
            json.dump([], sf)
            sf.truncate()
            cf.seek(0)
            json.dump(commits, cf, indent=2)
            cf.truncate()
            bf.seek(0)
            json.dump(branches, bf, indent=2)
            bf.truncate()

            print(f"Committed with ID {commit_id} and message: '{message}'")

    def kazi_commit_history(self):
        """View commit history."""
        if not os.path.exists(self.kazi_dir):
            print("Not a repository. Run 'kazi init' first.")
            return

        with open(self.commits_file, 'r') as f:
            commits = json.load(f)

        if not commits:
            print("No commits yet.")
        else:
            for commit in commits:
                print(f"ID: {commit['id']}, Message: {commit['message']}, Timestamp: {commit['timestamp']}")

    def kazi_create_branch(self, branch_name):
        """Create a new branch."""
        if not os.path.exists(self.kazi_dir):
            print("Not a repository. Run 'kazi init' first.")
            return

        with open(self.branches_file, 'r+') as f:
            branches = json.load(f)

            if branch_name in branches:
                print(f"Branch '{branch_name}' already exists.")
                return

            branches[branch_name] = {'commits': [], 'active': False}

            f.seek(0)
            json.dump(branches, f, indent=2)
            f.truncate()

            print(f"Branch '{branch_name}' created.")

    def kazi_checkout(self, branch_name):
        """Checkout to a different branch."""
        if not os.path.exists(self.kazi_dir):
            print("Not a repository. Run 'kazi init' first.")
            return

        with open(self.branches_file, 'r+') as f:
            branches = json.load(f)

            if branch_name not in branches:
                print(f"Branch '{branch_name}' does not exist.")
                return

            for branch in branches:
                branches[branch]['active'] = False

            branches[branch_name]['active'] = True

            f.seek(0)
            json.dump(branches, f, indent=2)
            f.truncate()

            print(f"Checked out to branch '{branch_name}'.")

    def kazi_merge(self, source_branch, target_branch):
        """Merge two branches."""
        if not os.path.exists(self.kazi_dir):
            print("Not a repository. Run 'kazi init' first.")
            return

        with open(self.branches_file, 'r+') as f:
            branches = json.load(f)

            if source_branch not in branches or target_branch not in branches:
                print(f"One or both branches '{source_branch}' or '{target_branch}' do not exist.")
                return

            source_commits = branches[source_branch]['commits']
            target_commits = branches[target_branch]['commits']

            conflicts = [commit for commit in source_commits if commit in target_commits]
            if conflicts:
                print(f"Merge conflict detected with commits: {conflicts}")
                resolution = input("Resolve by keeping (s)ource, (t)arget, or (s)kip? ")

                for conflict in conflicts:
                    if resolution == 's':
                        source_commits.remove(conflict)
                    elif resolution == 't':
                        continue
                    else:
                        print(f"Skipping conflict commit: {conflict}")

            branches[target_branch]['commits'].extend(commit for commit in source_commits if commit not in target_commits)

            f.seek(0)
            json.dump(branches, f, indent=2)
            f.truncate()

            print(f"Branch '{source_branch}' merged into '{target_branch}'.")

    def kazi_diff(self, branch1, branch2):
        """Show differences between branches."""
        if not os.path.exists(self.kazi_dir):
            print("Not a repository. Run 'kazi init' first.")
            return

        with open(self.branches_file, 'r') as f:
            branches = json.load(f)

        if branch1 not in branches or branch2 not in branches:
            print(f"One or both branches '{branch1}' or '{branch2}' do not exist.")
            return

        commits1 = set(branches[branch1]['commits'])
        commits2 = set(branches[branch2]['commits'])

        print(f"Commits only in {branch1}: {commits1 - commits2}")
        print(f"Commits only in {branch2}: {commits2 - commits1}")

    def kazi_clone(self, project_name, destination):
        """Clone a repository."""
        source_dir = os.path.join(self.repo_path, f".{project_name}")
        if not os.path.exists(source_dir):
            print(f"Repository '{project_name}' does not exist.")
            return

        destination_dir = os.path.join(destination, f".{project_name}")
        if os.path.exists(destination_dir):
            print(f"Destination '{destination_dir}' already exists.")
            return

        os.makedirs(destination_dir)
        for filename in os.listdir(source_dir):
            with open(os.path.join(source_dir, filename), 'r') as src:
                with open(os.path.join(destination_dir, filename), 'w') as dst:
                    dst.write(src.read())

        print(f"Cloned repository '{project_name}' to '{destination_dir}'.")


def main():
    parser = argparse.ArgumentParser(description="Kazi - A lightweight source control system")
    parser.add_argument('command', choices=['init', 'add', 'commit', 'commit-history', 'create-branch', 'checkout', 'merge', 'diff', 'clone'],
                        help="The command to run.")
    parser.add_argument('project_name', nargs='?', help="The project name.")
    parser.add_argument('file_path', nargs='?', help="The file path for add.")
    parser.add_argument('message', nargs='?', help="Commit message.")
    parser.add_argument('branch_name', nargs='?', help="Branch name.")
    parser.add_argument('source_branch', nargs='?', help="Source branch for merge.")
    parser.add_argument('target_branch', nargs='?', help="Target branch for merge.")
    parser.add_argument('destination', nargs='?', help="Destination directory for cloning.")

    args = parser.parse_args()

    kazi = Kazi()

    if args.command == 'init' and args.project_name:
        kazi.kazi_init(args.project_name)
    elif args.command == 'add' and args.file_path:
        kazi.kazi_add(args.file_path)
    elif args.command == 'commit' and args.message:
        kazi.kazi_commit(args.message)
    elif args.command == 'commit-history':
        kazi.kazi_commit_history()
    elif args.command == 'create-branch' and args.branch_name:
        kazi.kazi_create_branch(args.branch_name)
    elif args.command == 'checkout' and args.branch_name:
        kazi.kazi_checkout(args.branch_name)
    elif args.command == 'merge' and args.source_branch and args.target_branch:
        kazi.kazi_merge(args.source_branch, args.target_branch)
    elif args.command == 'diff' and args.branch1 and args.branch2:
        kazi.kazi_diff(args.branch1, args.branch2)
    elif args.command == 'clone' and args.project_name and args.destination:
        kazi.kazi_clone(args.project_name, args.destination)
    else:
        print("Invalid command or arguments.")


if __name__ == "__main__":
    main()
