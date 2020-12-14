
import filecmp
import os
import subprocess

GIT_DIFF_FILE_NAME = "diff.patch"
GOLDEN_DIFF_FILE_NAME = ".golden.diff"

def exec(args, cwd=None, print_stdout=False, ignore_error=False):
  r = subprocess.run(
      args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
  )
  if print_stdout:
    print(r.stdout.decode())
  if not ignore_error:
    print(r.stderr.decode())
  if not ignore_error and r.returncode != 0:
    r.check_returncode()
  return r.stdout.decode()


def validate_envs(envs):
  for env in envs:
    if os.getenv(env) is None:
      raise Exception("Error: the environment variable is missing: {}.".format(env))


def validate_result(git_diff, package_dir):
  golden_diff_path = os.path.join(package_dir, GOLDEN_DIFF_FILE_NAME)

  if len(git_diff) == 0:
    if not os.path.exists(golden_diff_path) or os.stat(golden_diff_path).st_size == 0:
      return 0
    print("The function is supposed to update the configs as the golden "
          "diff shows, but no changes were made. Please check the {} "
          "file.".format(GOLDEN_DIFF_FILE_NAME))
    return 1
  if not os.path.exists(golden_diff_path):
    print("Error: file {} is missing".format(GOLDEN_DIFF_FILE_NAME))
    return 1
  git_diff_path = os.path.join(package_dir, GIT_DIFF_FILE_NAME)
  write_to_file(git_diff_path, git_diff)
  if filecmp.cmp(git_diff_path, golden_diff_path):
    return 0
  print("Expected diff is shown in {} file, but got {}".format(GOLDEN_DIFF_FILE_NAME, git_diff))
  return 1


def write_to_file(path, content):
  file = open(path, "w")
  file.write(content)
  file.close()


def read_from_file(path):
  file = open(path, "r")
  content = file.read()
  file.close()
  return content


class Git():
  def __init__(self, dir):
    self.dir = dir
    self.bin = "git"
    self.exec(["config", "--global", "user.name", "blueprint-validator"])
    self.exec(["config", "--global", "user.email", "blueprint-validator@krm-blueprint.com"])

  def __repr__(self):
    return "Git:" + exec(["which", "git"])

  def exec(self, args):
    return exec([self.bin] + args, cwd=self.dir).strip()

  def init(self):
    self.exec(["init"])

  def commit(self, message):
    self.exec(["add", "-A"])
    self.exec(["commit", "-m", message])

  def diff(self, path):
    # add all files to capture untracked changes
    self.exec(["add", "-A"])
    return self.exec(["diff", "--cached", path])