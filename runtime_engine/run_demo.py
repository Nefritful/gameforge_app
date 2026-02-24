from runtime_engine.engine.app import run

# пример: run("storage/user_projects/nefritful@gmail.com/first")
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m runtime_engine.run_demo <project_dir>")
        raise SystemExit(2)
    run(sys.argv[1])
