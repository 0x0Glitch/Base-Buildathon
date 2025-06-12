// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "../lib/openzeppelin-contracts/contracts/token/ERC20/ERC20.sol";
import "../lib/openzeppelin-contracts/contracts/access/Ownable.sol";

//implements the erc7802compliance-should have an crosschainmint and crosschainburn function

interface IERC7802 {
    function crosschainMint(address to, uint256 amount) external;

    function crosschainBurn(address from, uint256 amount) external;
}

contract SuperETH is ERC20, IERC7802, Ownable {
    address public immutable aiAgent; // AI agent wallet (same across all chains)acts as an bridge which can transfer the supereth across chains

    event Deposited(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);
    event CrosschainMinted(address indexed receiver, uint256 amount);
    event CrosschainBurned(address indexed from, uint256 amount);

    constructor(
        address _aiAgent,
        address _owner
    ) ERC20("SuperETH", "sETH") Ownable(_owner) {
        aiAgent = _aiAgent;
    }

    //only agent will be able to call these functions
    //except deposit
    // whoever send eth to the contract will receive equal amount of the superETH
    /// @notice User deposits ETH and receives SuperETH (1:1 ratio)
    function deposit() external payable {
        require(msg.value > 0, "Amount must be greater than zero");

        _mint(msg.sender, msg.value);
        emit Deposited(msg.sender, msg.value);
    }

    /// @notice User burns SuperETH and withdraws native ETH
    function withdraw(uint256 amount) external {
        //checks all the necessary conditions if user wants to withdraw its eth
        require(amount > 0, "Amount must be greater than zero");
        require(balanceOf(msg.sender) >= amount, "Insufficient sETH balance");
        require(address(this).balance >= amount, "Insufficient reserves");

        _burn(msg.sender, amount);
        payable(msg.sender).transfer(amount);

        emit Withdrawn(msg.sender, amount);
    }

    /// @notice Only the AI agent can mint SuperETH cross-chain
    function crosschainMint(address to, uint256 amount) external override {
        require(msg.sender == aiAgent, "Unauthorized: Only AI agent can mint");
        _mint(to, amount);
        emit CrosschainMinted(to, amount);
    }

    /// @notice Only the AI agent can burn SuperETH cross-chain
    function crosschainBurn(address from, uint256 amount) external override {
        require(msg.sender == aiAgent, "Unauthorized: Only AI agent can burn");
        require(balanceOf(from) >= amount, "Insufficient balance");

        _burn(from, amount);
        emit CrosschainBurned(from, amount);
    }
}
