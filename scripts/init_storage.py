from pathlib import Path

def main():
    root = Path(__file__).resolve().parents[1] / "storage" / "user_projects"
    root.mkdir(parents=True, exist_ok=True)
    print("OK:", root)

if __name__ == "__main__":
    main()
