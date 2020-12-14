# Lint as: python3
"""The entry of E2E tests for catalog functions.
"""

import os
import sys
import tempfile
import lib

# Retrieve environment variables
try:
  lib.validate_envs(["GITHUB_REPOSITORY", "BLUEPRINT_DIRECTORY", "VALIDATE_PACKAGES", "PACKAGES_NEED_NETWORK_FLAG", "PACKAGES_NEED_PGP"])
except Exception as inst:
  print(inst)
  sys.exit(1)

REPO_URL = "https://github.com/{}".format(os.getenv("GITHUB_REPOSITORY"))
BP_DIR = os.getenv("BLUEPRINT_DIRECTORY")
VALIDATE_PACKAGES = [item.strip() for item in os.getenv("VALIDATE_PACKAGES").split(",")]
PACKAGES_NEED_NETWORK_FLAG = set([item.strip() for item in os.getenv("PACKAGES_NEED_NETWORK_FLAG").split(",")])
PACKAGES_NEED_PGP = set([item.strip() for item in os.getenv("PACKAGES_NEED_PGP").split(",")])

# Set up temp dir for the downloaded packages
# tmp_dir = tempfile.TemporaryDirectory(prefix="e2e_")
tmp_dir = os.path.join(tempfile.gettempdir(), "e2e")
lib.exec(["rm", "-rf", tmp_dir])
os.makedirs(tmp_dir)

git = lib.Git(tmp_dir)
git.init()

hasError = False

for package in VALIDATE_PACKAGES:
  print("==========Validating package {}==========".format(package))
  package_url = "{}/{}/{}".format(REPO_URL, BP_DIR, package)
  package_dir = os.path.join(tmp_dir, package)
  lib.exec(["kpt", "pkg", "get", package_url, package_dir])
  git.commit("original package {}".format(package))

  results_dir = os.path.join(package_dir, "results")
  os.makedirs(results_dir, exist_ok=True)
  if package in PACKAGES_NEED_PGP:
    os.environ["SOPS_IMPORT_PGP"] = lib.read_from_file(os.path.join(package_dir, "key.asc"))
  args = ["kpt", "fn", "run", package_dir, "--results-dir", results_dir]
  if package in PACKAGES_NEED_NETWORK_FLAG:
    args.append("--network")
  lib.exec(args, ignore_error=True)

  git_diff = git.diff(package_dir)
  validate_result = lib.validate_result(git_diff, package_dir)
  if validate_result == 0:
    print("Successfully validated package {}".format(package))
  else:
    hasError = True

  print("==========Finished validating package {}==========\n".format(package))

if hasError:
  sys.exit(1)