import os
import subprocess
import json

if __name__ == "__main__":
    if os.path.exists("./dist"):
        subprocess.run(["rm", "-rf", "./dist"])
    
    with open("./keys.json") as f:
        key = json.load(f)["PYPI_KEY"]

    subprocess.run(["python3", "setup.py", "sdist", "bdist_wheel"])

    subprocess.run(["twine", "upload", "--skip-existing", "--repository", "pypi", "dist/*", "-u", "__token__", "-p", key])

