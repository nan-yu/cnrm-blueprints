
import os

REPO_URL = "REPO_URL"
BLUEPRINT_DIRECTORY = "BLUEPRINT_DIRECTORY"
PACKAGES = "VALIDATE_PACKAGES"

envs = [REPO_URL, BLUEPRINT_DIRECTORY, PACKAGES]


def validate():
  for env in envs:
    if os.getenv(env) is None:
      raise Exception("Error: the environment variable is missing: {}.".format(env))
