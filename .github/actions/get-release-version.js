const input_title = process.env.INPUT_RELEASE_TITLE;
const regex = /Release ([\d.]+)/gm;

const matches = regex.exec(input_title);
const version = matches[1];
if (version) {
  console.log(`::set-output name=version::${version}`);
} else {
  throw new Error(`No version found in release title: ${input_title}`);
}
