# Lint as: python3
"""The entry of E2E tests for catalog functions.
"""

import os
import sys
import tempfile
import env
import lib
from package import *

# Retrieve environment variables
try:
  env.validate()

  repo_url = os.getenv(env.REPO_URL)
  bp_dir = os.getenv(env.BLUEPRINT_DIRECTORY)
  packages = [item.strip() for item in os.getenv(env.PACKAGES).split(",")]

  # Set up temp dir for the downloaded packages
  # tmp_dir = tempfile.TemporaryDirectory(prefix="e2e_")
  tmp_dir = os.path.join(tempfile.gettempdir(), "e2e")
  lib.exec(["rm", "-rf", tmp_dir], print_stdout=False)
  os.makedirs(tmp_dir)

  git = lib.Git(tmp_dir)
  git.init()

  for p in packages:
    print("==========Validating package {}==========".format(p))
    pkg = Package(repo_url, bp_dir, tmp_dir, p, git)
    print(pkg)
    pkg.prepare()
    pkg.run_function()
    pkg.validate_function_result()
    print("==========Successfully validated package {}==========\n".format(p))

except Exception as e:
  print(e)
  sys.exit(1)