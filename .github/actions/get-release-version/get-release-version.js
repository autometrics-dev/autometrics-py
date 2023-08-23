const branchName = process.env.GITHUB_REF;
const regex = /release\/([\d.]+)/gm;

const matches = regex.exec(branchName);
const version = matches[1];
if (version) {
  console.log(`::set-output name=version::${version}`);
} else {
  throw new Error(`No version found in release title: ${input_title}`);
}
