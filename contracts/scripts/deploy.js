const { ethers } = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  const [deployer] = await ethers.getSigners();

  console.log("Deploying MantisAgentIdentity to Mantle Testnet...");
  console.log("Deployer wallet:", deployer.address);
  console.log(
    "Balance:",
    ethers.formatEther(await ethers.provider.getBalance(deployer.address)),
    "MNT"
  );

  const MantisAgentIdentity = await ethers.getContractFactory("MantisAgentIdentity");

  const contract = await MantisAgentIdentity.deploy(
    deployer.address,                                           
    "Zeham",                                               
    "1.0.0",                                                    
    "AI-powered on-chain security monitor for Mantle Network"  
  );

  await contract.waitForDeployment();
  const address = await contract.getAddress();

  console.log("\n✅ MantisAgentIdentity deployed to:", address);
  console.log("   Network:    Mantle Testnet (chainId: 5003)");
  console.log("   Explorer:  ", `https://explorer.sepolia.mantle.xyz/address/${address}`);
  console.log("\n👉 Add this to the backend/.env:");
  console.log(`   ERC8004_CONTRACT_ADDRESS=${address}`);

  // Export ABI for backend use.
  const artifact = require(`../artifacts/contracts/MantisAgentIdentity.sol/MantisAgentIdentity.json`);
  const abiPath = path.join(__dirname, "../abis/MantisAgentIdentity.json");
  fs.mkdirSync(path.dirname(abiPath), { recursive: true });
  fs.writeFileSync(abiPath, JSON.stringify(artifact.abi, null, 2));
  console.log("\n📄 ABI exported to: contracts/abis/MantisAgentIdentity.json");

  const backendAbiPath = path.join(__dirname, "../../backend/abis/MantisAgentIdentity.json");
  fs.mkdirSync(path.dirname(backendAbiPath), { recursive: true });
  fs.writeFileSync(backendAbiPath, JSON.stringify(artifact.abi, null, 2));
  console.log("📄 ABI also copied to: backend/abis/MantisAgentIdentity.json");

  // Write deployment record.
  const record = {
    network: "mantleTestnet",
    chainId: 5003,
    address,
    deployer: deployer.address,
    timestamp: new Date().toISOString(),
    explorer: `https://explorer.sepolia.mantle.xyz/address/${address}`
  };
  const deploymentsDir = path.join(__dirname, "../deployments");
  fs.mkdirSync(deploymentsDir, { recursive: true });
  fs.writeFileSync(
    path.join(deploymentsDir, "testnet.json"),
    JSON.stringify(record, null, 2)
  );
  console.log("\n📝 Deployment record: contracts/deployments/testnet.json");
  console.log("\nNext: verify the contract with");
  console.log(`   npm run verify:testnet -- ${address} ${deployer.address} Zeham 1.0.0 "AI-powered on-chain security monitor for Mantle Network"`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
