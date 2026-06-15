const { ethers } = require("hardhat");

async function main() {
    const [deployer] = await ethers.getSigners();
    const Factory = await ethers.getContractFactory("FlashLoanSimulator");
    const contract = await Factory.deploy();
    await contract.waitForDeployment();
    const address = await contract.getAddress();
    console.log("FlashLoanSimulator deployed to:", address);
    console.log("Add to watchlist:", address);
}
main().catch(console.error);