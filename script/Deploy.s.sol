// SPDX-License-Identifier: UNLICENSED
pragma solidity >=0.8.10;

import "forge-std/Script.sol";
import "../src/UnstoppableModelErc20.sol";
import "./Deployment.sol";

// It deploys all contracts.
contract Deploy is Deployment, Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(deployerPrivateKey);

        bytes memory args = abi.encode("UnstoppableModelErc20", "UMC", 18);
        UnstoppableModelErc20 token = UnstoppableModelErc20(_deployContract("UnstoppableModelErc20", "UnstoppableModelErc20", args));

        _printDeployments();

        vm.stopBroadcast();
    }
}

