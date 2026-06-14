require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config({ path: "../backend/.env" });

const AGENT_KEY = process.env.AGENT_PRIVATE_KEY;
const accounts = AGENT_KEY ? [AGENT_KEY] : [];

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      }
    }
  },
  networks: {
    // ── Mantle Testnet (Sepolia-based) ─────────────────────────────────────
    mantleTestnet: {
      url:      "https://rpc.sepolia.mantle.xyz",
      chainId:  5003,
      accounts,
      gasPrice: "auto"
    },
    // ── Mantle Mainnet ─────────────────────────────────────────────────────
    mantleMainnet: {
      url:      "https://rpc.mantle.xyz",
      chainId:  5000,
      accounts,
      gasPrice: "auto"
    }
  },
  etherscan: {
    apiKey: {
      mantleTestnet: process.env.MANTLE_EXPLORER_API_KEY || "placeholder",
      mantleMainnet: process.env.MANTLE_EXPLORER_API_KEY || "placeholder"
    },
    customChains: [
      {
        network: "mantleTestnet",
        chainId: 5003,
        urls: {
          apiURL:     "https://explorer.sepolia.mantle.xyz/api",
          browserURL: "https://explorer.sepolia.mantle.xyz"
        }
      },
      {
        network: "mantleMainnet",
        chainId: 5000,
        urls: {
          apiURL:     "https://explorer.mantle.xyz/api",
          browserURL: "https://explorer.mantle.xyz"
        }
      }
    ]
  }
};
