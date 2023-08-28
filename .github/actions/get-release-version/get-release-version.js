const fs = require("fs");
const path = require("path");
const regex = /version = "([\d.]+)"/gm;

const file_path = path.join(process.env.GITHUB_WORKSPACE, "pyproject.toml");
const file_contents = fs.readFileSync(file_path, { encoding: "utf8" });
const matches = regex.exec(file_contents);
if (matches && matches.length == 2) {
  const [_, version] = matches;

  fs.appendFileSync(process.env.GITHUB_OUTPUT, `version=${version}`, {
    encoding: "utf8",
  });
} else {
  throw new Error(`No version found in ${file_path}`);
}
