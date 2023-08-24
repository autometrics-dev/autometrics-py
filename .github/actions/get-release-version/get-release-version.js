const branchName = process.env.GITHUB_REF;
const regex = /release\/([\d.]+)/gm;

const matches = regex.exec(branchName);
if (matches && matches.length == 2) {
  const [_, version] = matches;
  const fs = require("fs");

  fs.appendFileSync(process.env.GITHUB_OUTPUT, `version=${version}`, {
    encoding: "utf8",
  });
} else {
  throw new Error(`No version found in release title: ${input_title}`);
}
