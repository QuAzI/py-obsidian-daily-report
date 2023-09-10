import os
import datetime
import subprocess


PROJECTS_DIR = "."
VAULT_DIR = "worklog"
report_date = datetime.datetime.today()

def write_report(file_path: str, report: str):
    with open(file_path, "a") as f:
        daily_file_has_notes = os.path.isfile(file_path)
        if daily_file_has_notes:
            f.write(f"\n---\n")
        
        f.write(f"planned:: {report}\n")

def write_to_obsidian(vault_dir: str, report: str):
    if not os.path.exists(vault_dir):
        raise Exception('No Obsidian vault present')
    
    file_path = os.path.join(vault_dir, f"{report_date.strftime('%Y-%m-%d')}.md")
    write_report(file_path, report)

def write_repo_stat_to_obsidian(repo_dir: str, vault_dir: str):
    git_command = [
        "git", 
        "log", 
        "--all", 
        "--author-date-order", 
        "--author=$(git config user.email)", 
        "--no-merges", 
        "--pretty=\"%ad  %w(0,0,24)%s\"", 
        "--date=format:'%Y-%m-%d %H:%M'", 
        f"--since='{report_date.strftime('%Y-%m-%d')}'", 
        f"--until='{report_date.strftime('%Y-%m-%d')} 23:59:59'"]
    
    git_output = subprocess.check_output(git_command).decode('utf-8')

    report = set(git_output.split('\r\n'))
    report.sort()

    write_to_obsidian(vault_dir, git_output)

if __name__ == "__main__":
    vault_dir = os.environ.get("OBSIDIAN_VAULT", VAULT_DIR)

    projects_dir = os.environ.get("projects", ".")
    if not os.path.exists(projects_dir):
        raise Exception('No Projects present')

    (root, dirs, _) = os.walk(projects_dir)
    for repo_dir in dirs:
        if not os.path.exists(".git"):
            continue
        
        write_repo_stat_to_obsidian(repo_dir, vault_dir)
