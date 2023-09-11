import os
import datetime
import subprocess

PROJECTS_DIR_DEFAULT = "."
VAULT_DIR_DEFAULT = "worklog"
REPORT_DATE_DEFAULT = datetime.datetime.today()


def write_report(file_path: str, report: list[str]):
    lines: list[str] = []
    daily_file_has_notes = os.path.isfile(file_path)
    if daily_file_has_notes:
        with open(file_path, "r", encoding='utf-8') as f:
            lines = [line.strip() for line in set(f.readlines())]

    new_lines = [line for line in report if line not in lines]

    if len(new_lines) == 0:
        print("Report already present")
        return

    with open(file_path, "a", encoding='utf-8', newline=os.linesep) as f:
        if daily_file_has_notes:
            print('', file=f)
            print('', file=f)
            print('---', file=f)
            print('', file=f)

        for line in new_lines:
            print(line, file=f)


def write_to_obsidian(vault_dir: str, report: list[str]):
    if not os.path.exists(vault_dir):
        raise Exception(f'No Obsidian vault present: {vault_dir}')

    file_path = os.path.join(vault_dir, f"{REPORT_DATE_DEFAULT.strftime('%Y-%m-%d')}.md")
    write_report(file_path, report)


def write_repo_stat_to_obsidian(repo_dir: str, vault_dir: str):
    user_email = subprocess.check_output("git config user.email", cwd=repo_dir).decode(
        'utf-8').strip()

    git_command = [
        'git',
        'log',
        '--all',
        '--author-date-order',
        f'--author={user_email}',
        '--no-merges',
        '--pretty=%ad  %w(0,0,24)%s',
        "--date=format:%Y-%m-%d %H:%M",
        f'--since={REPORT_DATE_DEFAULT.strftime("%Y-%m-%d")} 00:00:00',
        f'--until={REPORT_DATE_DEFAULT.strftime("%Y-%m-%d")} 23:59:59'
    ]

    git_output = subprocess.check_output(git_command, cwd=repo_dir)

    if git_output is None:
        return

    commits_list = [line.strip() for line in git_output.decode('utf-8').split('\n')
                    if len(line) > 0]
    commits_list.sort()

    report = list(set(commits_list))

    write_to_obsidian(vault_dir, report)


if __name__ == "__main__":
    vault = os.environ.get("OBSIDIAN_VAULT", VAULT_DIR_DEFAULT)

    projects_dir = os.environ.get("projects", ".")
    if not os.path.exists(projects_dir):
        raise Exception(f'No Projects present: {projects_dir}')

    dirs = [os.path.join(projects_dir, f.name) for f in os.scandir(projects_dir)
            if f.is_dir() and os.path.exists(os.path.join(f.name, '.git'))]
    for repo in dirs:
        write_repo_stat_to_obsidian(repo, vault)
