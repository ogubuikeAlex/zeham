const fs = require("fs");
const path = require("path");

const ARTIFACT = path.join(
  __dirname,
  "../artifacts/contracts/MantisAgentIdentity.sol/MantisAgentIdentity.json"
);

function main() {
  if (!fs.existsSync(ARTIFACT)) {
    console.error("❌ Artifact not found. Run `npm run compile` first.");
    process.exit(1);
  }
  const artifact = JSON.parse(fs.readFileSync(ARTIFACT, "utf8"));
  const targets = [
    path.join(__dirname, "../abis/MantisAgentIdentity.json"),
    path.join(__dirname, "../../backend/abis/MantisAgentIdentity.json"),
  ];
  for (const target of targets) {
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.writeFileSync(target, JSON.stringify(artifact.abi, null, 2));
    console.log("📄 ABI exported to:", path.relative(path.join(__dirname, ".."), target));
  }
}

main();
