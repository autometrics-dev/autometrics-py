const branchName = process.env.GITHUB_REF;
const regex = /release\/([\d.]+)/gm;

const matches = regex.exec(branchName);
const version = matches[1];
if (version) {
  const fs = require("fs");

  fs.appendFileSync(process.env.GITHUB_STATE, `VERSION=${version}`, {
    encoding: "utf8",
  });
} else {
  throw new Error(`No version found in release title: ${input_title}`);
}
