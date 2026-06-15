const { ethers } = require("hardhat");
const fs = require("fs"), path = require("path");

async function main() {
  const [deployer] = await ethers.getSigners();
  const balance = await ethers.provider.getBalance(deployer.address);

  console.log("⚠️  MAINNET DEPLOYMENT — Mantle Mainnet (chainId: 5000)");
  console.log("Deployer:", deployer.address);
  console.log("Balance: ", ethers.formatEther(balance), "MNT");

  if (balance < ethers.parseEther("0.01")) {
    throw new Error("Insufficient MNT balance. Fund the agent wallet before deploying to mainnet.");
  }

  const MantisAgentIdentity = await ethers.getContractFactory("MantisAgentIdentity");
  const contract = await MantisAgentIdentity.deploy(
    deployer.address,
    "Zeham",
    "1.0.0",
    "AI-powered on-chain security monitor for Mantle Network"
  );

  await contract.waitForDeployment();
  const address = await contract.getAddress();

  console.log("\n✅ Mainnet deployment complete:", address);
  console.log("   Explorer: https://explorer.mantle.xyz/address/" + address);

  const artifact = require(`../artifacts/contracts/MantisAgentIdentity.sol/MantisAgentIdentity.json`);
  for (const abiPath of [
    path.join(__dirname, "../abis/MantisAgentIdentity.json"),
    path.join(__dirname, "../../backend/abis/MantisAgentIdentity.json"),
  ]) {
    fs.mkdirSync(path.dirname(abiPath), { recursive: true });
    fs.writeFileSync(abiPath, JSON.stringify(artifact.abi, null, 2));
  }

  const record = {
    network: "mantleMainnet", chainId: 5000, address,
    deployer: deployer.address, timestamp: new Date().toISOString(),
    explorer: `https://explorer.mantle.xyz/address/${address}`
  };
  fs.mkdirSync(path.join(__dirname, "../deployments"), { recursive: true });
  fs.writeFileSync(
    path.join(__dirname, "../deployments/mainnet.json"),
    JSON.stringify(record, null, 2)
  );

  console.log("\n👉 Update backend/.env:");
  console.log(`   ERC8004_CONTRACT_ADDRESS=${address}`);
  console.log("   ERC8004_NETWORK=mainnet");
  console.log("   MANTLE_EXPLORER_BASE=https://explorer.mantle.xyz");
}

main().catch(err => { console.error(err); process.exit(1); });
