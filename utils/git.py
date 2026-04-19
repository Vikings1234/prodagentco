"""Git helpers shared across pipeline entry points."""
import datetime
import subprocess

from config.settings import BASE_DIR


def commit_and_push_outputs(label: str = "Pipeline run") -> None:
    """Commit and push the outputs/ folder to GitHub regardless of verdict."""
    try:
        subprocess.run(
            ["git", "add", "outputs/"],
            check=True, capture_output=True, cwd=BASE_DIR,
        )
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subprocess.run(
            ["git", "commit", "-m", f"{label} — {timestamp}"],
            check=True, capture_output=True, cwd=BASE_DIR,
        )
        subprocess.run(
            ["git", "push"],
            check=True, capture_output=True, cwd=BASE_DIR,
        )
    except subprocess.CalledProcessError as e:
        print(f"Git operation failed: {e}")
        print(f"Error output: {e.stderr.decode() if e.stderr else 'None'}")
