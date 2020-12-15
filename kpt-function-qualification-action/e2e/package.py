
import filecmp
import os
import lib

HTTP_PREFIX = "http"
GIT_DIFF_FILE_NAME = "diff.patch"
GOLDEN_DIFF_FILE_NAME = ".golden.diff"
FLAGS_FILE_NAME = ".flags"


class Package:
  def __init__(self, repo_url, bp_dir, tmp_dir, package, git):
    self.repo_url = repo_url
    self.package = package
    self.pkg_tmp_dir = os.path.join(tmp_dir, package)
    self.pkg_source_path = os.path.join(repo_url, bp_dir, package)
    self.git = git

  def __repr__(self):
    return "test package:\n\trepo_url: {}\n\tpackage: {}\n\t" \
           "package_source_path: {}\n\tpackage_tmp_dir: {}"\
      .format(self.repo_url, self.package, self.pkg_source_path,
              self.pkg_tmp_dir)

  def prepare(self):
    if self.repo_url.startswith(HTTP_PREFIX):
      lib.exec(["kpt", "pkg", "get", self.pkg_source_path, self.pkg_tmp_dir])
    else:
      lib.exec("cp -r {} {}".format(self.pkg_source_path, self.pkg_tmp_dir), shell=True)
    self.git.commit("original package {}".format(self.package))

  def run_function(self):
    args = ["kpt", "fn", "run"]
    results_dir = os.path.join(self.pkg_tmp_dir, "results")
    os.makedirs(results_dir, exist_ok=True)

    flags_file = os.path.join(self.pkg_tmp_dir, FLAGS_FILE_NAME)
    if os.path.exists(flags_file):
      lines = lib.read_lines_from_file(flags_file)
      for line in lines:
        args.append(line)
    args.append(self.pkg_tmp_dir)
    args.append("--results-dir")
    args.append(results_dir)
    lib.exec(" ".join(args), shell=True, ignore_error=True)

  def validate_function_result(self):
    git_diff = self.git.diff(self.pkg_tmp_dir)
    golden_diff_path = os.path.join(self.pkg_tmp_dir, GOLDEN_DIFF_FILE_NAME)

    if len(git_diff) == 0:
      if not os.path.exists(golden_diff_path) or os.stat(golden_diff_path).st_size == 0:
        return
      raise Exception("The function is supposed to update the configs as the golden "
            "diff shows, but no changes were made. Please check the {} "
            "file.".format(GOLDEN_DIFF_FILE_NAME))
    if not os.path.exists(golden_diff_path):
      raise Exception("Error: file {} is missing".format(GOLDEN_DIFF_FILE_NAME))
    git_diff_path = os.path.join(self.pkg_tmp_dir, GIT_DIFF_FILE_NAME)
    lib.write_to_file(git_diff_path, git_diff)
    if not filecmp.cmp(git_diff_path, golden_diff_path):
      raise Exception("Expected diff is shown in {} file, but got {}".format(GOLDEN_DIFF_FILE_NAME, git_diff))

