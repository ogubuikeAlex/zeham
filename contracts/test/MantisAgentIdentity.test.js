// contracts/test/MantisAgentIdentity.test.js
const { expect } = require("chai");
const { ethers } = require("hardhat");
const { anyValue } = require("@nomicfoundation/hardhat-chai-matchers/withArgs");

describe("MantisAgentIdentity", function () {
  let contract, owner, other;

  beforeEach(async function () {
    [owner, other] = await ethers.getSigners();
    const Factory = await ethers.getContractFactory("MantisAgentIdentity");
    contract = await Factory.deploy(
      owner.address, "Zeham", "1.0.0", "Test deployment"
    );
    await contract.waitForDeployment();
  });

  it("should set agent identity correctly on deploy", async function () {
    const identity = await contract.getAgentIdentity();
    expect(identity.name).to.equal("Zeham");
    expect(identity.version).to.equal("1.0.0");
    expect(identity.agentWallet).to.equal(owner.address);
    expect(identity.decisionCount).to.equal(0n);
  });

  it("should log a decision and emit DecisionLogged event", async function () {
    const tx = await contract.logDecision(
      "flash_loan", "CRITICAL",
      "Possible flash loan attack detected", "0xContractTarget", true
    );
    const receipt = await tx.wait();
    expect(receipt.status).to.equal(1);
    expect(await contract.getDecisionCount()).to.equal(1n);
  });

  it("should store decision data correctly", async function () {
    await contract.logDecision("rug_pull", "HIGH", "Rug pull detected", "0xTarget", true);
    const decision = await contract.getDecision(0);
    expect(decision.anomalyType).to.equal("rug_pull");
    expect(decision.severity).to.equal("HIGH");
    expect(decision.contractTarget).to.equal("0xTarget");
    expect(decision.isAnomaly).to.equal(true);
  });

  it("should increment totalDecisions on each log", async function () {
    await contract.logDecision("whale", "MEDIUM", "Whale move", "0xA", false);
    await contract.logDecision("exploit", "CRITICAL", "Exploit detected", "0xB", true);
    expect(await contract.totalDecisions()).to.equal(2n);
  });

  it("should reject logDecision from non-owner", async function () {
    await expect(
      contract.connect(other).logDecision("none", "NONE", "Test", "0x0", false)
    ).to.be.revertedWithCustomError(contract, "OwnableUnauthorizedAccount");
  });

  it("should revert getDecision for out-of-range index", async function () {
    await expect(contract.getDecision(0)).to.be.revertedWith("Decision does not exist");
  });

  it("should return recent decisions correctly", async function () {
    for (let i = 0; i < 5; i++) {
      await contract.logDecision("exploit", "HIGH", `Decision ${i}`, "0xC", true);
    }
    const recent = await contract.getRecentDecisions(3);
    expect(recent.length).to.equal(3);
    expect(recent[2].reason).to.equal("Decision 4");
  });

  it("should emit DecisionLogged with all correct fields", async function () {
    await expect(
      contract.logDecision("wash_trade", "MEDIUM", "Wash trade detected", "0xD", true)
    ).to.emit(contract, "DecisionLogged")
      .withArgs(0n, owner.address, "wash_trade", "MEDIUM", "Wash trade detected", "0xD", anyValue, true);
  });
});
