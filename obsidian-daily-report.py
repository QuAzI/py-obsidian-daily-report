import os
import datetime
import subprocess


PROJECTS_DIR = "."
VAULT_DIR = "worklog"
report_date = datetime.datetime.today()

def write_report(file_path: str, report: str):
    print(file_path, report)
    # return

    with open(file_path, "a") as f:
        daily_file_has_notes = os.path.isfile(file_path)
        if daily_file_has_notes:
            f.write(f"\r\n---\r\n")
        
        f.write(f"{report}\r\n")

def write_to_obsidian(vault_dir: str, report: str):
    if not os.path.exists(vault_dir):
        raise Exception(f'No Obsidian vault present: {vault_dir}')
    
    file_path = os.path.join(vault_dir, f"{report_date.strftime('%Y-%m-%d')}.md")
    write_report(file_path, report)

def write_repo_stat_to_obsidian(repo_dir: str, vault_dir: str):
    user_email = subprocess.check_output("git config user.email", cwd=repo_dir).decode('utf-8').strip()

    git_command = [
        'git', 
        'log', 
        '--all', 
        '--author-date-order', 
        f'--author={user_email}', 
        '--no-merges', 
        '--pretty=%ad  %w(0,0,24)%s', 
        "--date=format:%Y-%m-%d %H:%M", 
        f'--since={report_date.strftime("%Y-%m-%d")} 00:00:00', 
        f'--until={report_date.strftime("%Y-%m-%d")} 23:59:59'
        ]
    
    # git_command = ["git", "log"]
    
    git_output = subprocess.check_output(git_command, cwd=repo_dir)

    if git_output is None:
        return

    commits_list = git_output.decode('utf-8').strip().split('\r\n')
    commits_list.sort()

    report = "\r\n".join(set(commits_list))

    write_to_obsidian(vault_dir, report)

if __name__ == "__main__":
    vault_dir = os.environ.get("OBSIDIAN_VAULT", VAULT_DIR)

    projects_dir = os.environ.get("projects", ".")
    if not os.path.exists(projects_dir):
        raise Exception(f'No Projects present: {projects_dir}')

    dirs = [os.path.join(projects_dir, f.name) for f in os.scandir(projects_dir) 
            if f.is_dir() and os.path.exists(os.path.join(f.name, '.git'))]
    for repo_dir in dirs:
        write_repo_stat_to_obsidian(repo_dir, vault_dir)
