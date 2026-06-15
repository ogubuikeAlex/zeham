// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title FlashLoanSimulator
 * @notice Simulates the event pattern of a flash loan attack for testing MantisSIEM.
 * @dev Deploy this to Mantle testnet. Call simulateAttack() to trigger the alert pipeline.
 */
contract FlashLoanSimulator {

    event FlashLoan(address indexed borrower, uint256 amount);
    event Swap(address indexed trader, uint256 amountIn, uint256 amountOut);
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Liquidation(address indexed target, uint256 debtAmount);

    /**
     * @notice Emits 4 different event types in a single transaction.
     * This pattern is exactly what FlashLoanRule in ADR-002 detects.
     * Call this function from your agent wallet.
     */
    function simulateFlashLoanAttack() external {
        emit FlashLoan(msg.sender, 1_000_000 ether);
        emit Swap(msg.sender, 1_000_000 ether, 999_000 ether);
        emit Transfer(msg.sender, address(this), 1_000_000 ether);
        emit Liquidation(msg.sender, 1_000 ether);
    }

    /**
     * @notice Simulates a rug pull — large liquidity removal from one address.
     */
    function simulateRugPull() external {
        for (uint i = 0; i < 5; i++) {
            emit Transfer(msg.sender, address(0), 200_000 ether);
        }
    }

    /**
     * @notice Simulates wash trading — same address buying and selling.
     */
    function simulateWashTrade() external {
        emit Swap(msg.sender, 100 ether, 99 ether);
        emit Swap(msg.sender, 99 ether, 100 ether);
        emit Swap(msg.sender, 100 ether, 99 ether);
        emit Swap(msg.sender, 99 ether, 100 ether);
    }
}