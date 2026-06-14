// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title MantisAgentIdentity
 * @notice ERC-8004 compliant agent identity contract for Zeham.
 *         Logs every AI security decision permanently on Mantle Network.
 * @dev Only the owner (the Zeham agent wallet) can log decisions.
 *      All decisions are queryable via the DecisionLogged event log.
 */
contract MantisAgentIdentity is Ownable {
    // ─── Agent Identity ─────────────────────────────────────────────────────

    string public agentName;
    string public agentVersion;
    string public agentDescription;
    uint256 public deployedAt;
    uint256 public totalDecisions;

    // ─── Decision Storage ────────────────────────────────────────────────────

    struct Decision {
        uint256 index;
        string anomalyType;
        string severity; 
        string reason; 
        string contractTarget;
        uint256 timestamp;
        bool isAnomaly;
    }

    Decision[] private decisions;

    event DecisionLogged(
        uint256 indexed index,
        address indexed agent,
        string anomalyType,
        string severity,
        string reason,
        string contractTarget,
        uint256 timestamp,
        bool isAnomaly
    );

    event AgentIdentityRegistered(
        address indexed agent,
        string name,
        string version,
        uint256 timestamp
    );

    constructor(
        address _agentWallet,
        string memory _name,
        string memory _version,
        string memory _description
    ) Ownable(_agentWallet) {
        agentName = _name;
        agentVersion = _version;
        agentDescription = _description;
        deployedAt = block.timestamp;
        totalDecisions = 0;

        emit AgentIdentityRegistered(
            _agentWallet,
            _name,
            _version,
            block.timestamp
        );
    }

    /**
     * @notice Log an agent decision on-chain.
     * @dev Only callable by the owner (the Zeham agent wallet).
     *      Called by backend/agent/chain.py after every alert is written.
     * @param _anomalyType  One of: flash_loan, rug_pull, whale, wash_trade, exploit, none
     * @param _severity     One of: CRITICAL, HIGH, MEDIUM, LOW, NONE
     * @param _reason       Human-readable reason string (keep under 200 chars to save gas)
     * @param _contractTarget  The monitored Mantle contract address
     * @param _isAnomaly    TRUE if an anomaly was detected, FALSE for clean scans
     */
    function logDecision(
        string calldata _anomalyType,
        string calldata _severity,
        string calldata _reason,
        string calldata _contractTarget,
        bool _isAnomaly
    ) external onlyOwner {
        uint256 index = decisions.length;

        decisions.push(
            Decision({
                index: index,
                anomalyType: _anomalyType,
                severity: _severity,
                reason: _reason,
                contractTarget: _contractTarget,
                timestamp: block.timestamp,
                isAnomaly: _isAnomaly
            })
        );

        totalDecisions++;

        emit DecisionLogged(
            index,
            msg.sender,
            _anomalyType,
            _severity,
            _reason,
            _contractTarget,
            block.timestamp,
            _isAnomaly
        );
    }

    /**
     * @notice Get a specific decision by index.
     */
    function getDecision(
        uint256 _index
    ) external view returns (Decision memory) {
        require(_index < decisions.length, "Decision does not exist");
        return decisions[_index];
    }

    /**
     * @notice Get the total number of decisions logged.
     */
    function getDecisionCount() external view returns (uint256) {
        return decisions.length;
    }

    /**
     * @notice Get the most recent N decisions (for dashboard use).
     * @param _count Number of recent decisions to return (max 50)
     */
    function getRecentDecisions(
        uint256 _count
    ) external view returns (Decision[] memory) {
        uint256 total = decisions.length;
        if (total == 0) return new Decision[](0);

        uint256 count = _count > 50 ? 50 : _count;
        count = count > total ? total : count;

        Decision[] memory recent = new Decision[](count);
        for (uint256 i = 0; i < count; i++) {
            recent[i] = decisions[total - count + i];
        }
        return recent;
    }

    /**
     * @notice Get agent metadata — for ERC-8004 compliance and dashboard display.
     */
    function getAgentIdentity()
        external
        view
        returns (
            string memory name,
            string memory version,
            string memory description,
            address agentWallet,
            uint256 deployedTimestamp,
            uint256 decisionCount
        )
    {
        return (
            agentName,
            agentVersion,
            agentDescription,
            owner(),
            deployedAt,
            totalDecisions
        );
    }
}
