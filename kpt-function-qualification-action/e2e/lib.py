
import os
import subprocess


def exec(args, env=None, cwd=None, shell=False, print_stdout=True, ignore_error=False):
  if env is None:
    env = os.environ.copy()
  r = subprocess.run(
      args, env=env, cwd=cwd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE
  )
  if print_stdout:
    if shell:
      print("running '%s'" % (args))
    else:
      print("running '%s'" % (" ".join(args)))
    stdout_bytes = r.stdout.decode()
    if len(stdout_bytes) > 0:
      print(stdout_bytes)

  stderr_bytes = r.stderr.decode()
  if len(stderr_bytes) > 0:
   print("stderr: '{}'".format(stderr_bytes.strip()))

  if not ignore_error and r.returncode != 0:
    r.check_returncode()
  return r.stdout.decode()


def write_to_file(path, content):
  file = open(path, "w")
  file.write(content)
  file.close()


def read_from_file(path):
  file = open(path, "r")
  content = file.read()
  file.close()
  return content


def read_lines_from_file(path):
  file = open(path, 'r')
  lines = file.readlines()
  file.close()
  return lines


class Git():
  def __init__(self, dir):
    self.dir = dir
    self.bin = "git"
    self.exec(["config", "--global", "user.name", "blueprint-validator"])
    self.exec(["config", "--global", "user.email", "blueprint-validator@krm-blueprint.com"])

  def __repr__(self):
    return "Git:" + exec(["which", "git"])

  def exec(self, args):
    return exec([self.bin] + args, cwd=self.dir, print_stdout=False).strip()

  def init(self):
    self.exec(["init"])

  def commit(self, message):
    self.exec(["add", "-A"])
    self.exec(["commit", "-m", message])

  def diff(self, path):
    # add all files to capture untracked changes
    self.exec(["add", "-A"])
    return self.exec(["diff", "--cached", path])