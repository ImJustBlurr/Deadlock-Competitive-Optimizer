import subprocess
import sys
import os

def build():
    script_name = "DeadlockCompetitiveOptimizer.py"

    for folder in ["build", "temp_build", "dist"]:
        if os.path.exists(folder):
            print(f"Removing folder: {folder}")
            import shutil
            shutil.rmtree(folder)

    cmd = [
        "pyinstaller",
        "--onefile",
        "--distpath", ".",
        "--workpath", "temp_build",
        "--specpath", "temp_build",
        script_name,
    ]

    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print("Build succeeded!")
    else:
        print("Build failed!")

if __name__ == "__main__":
    build()