// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "../lib/forge-std/src/Script.sol";
import "../src/InterOp.sol";

contract DeployInterOp is Script {
    function run() public returns (SuperETH) {
        // Read environment variables
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address aiAgent = vm.envAddress("AI_AGENT_ADDRESS");
        address owner = vm.envAddress("OWNER_ADDRESS");

        // Start broadcasting transactions
        vm.startBroadcast(deployerPrivateKey);

        // Deploy the contract
        SuperETH superETH = new SuperETH(aiAgent, owner);

        // Stop broadcasting
        vm.stopBroadcast();

        // Log deployment information
        console2.log("SuperETH deployed to:", address(superETH));
        console2.log("AI Agent address:", aiAgent);
        console2.log("Owner address:", owner);

        return superETH;
    }
}
