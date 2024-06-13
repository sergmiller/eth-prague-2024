// SPDX-License-Identifier: UNLICENSED
pragma solidity >=0.8.10;

import "forge-std/Script.sol";
import "../src/UnstoppableModelErc20.sol";
import "../src/UnstoppableModel.sol";
import "./Deployment.sol";

// It deploys all contracts.
contract Deploy is Deployment, Script {
    string constant DEPLOYMENTS_PATH = "/deployments/";
    string private fullDeploymentsPath;

    function setUp() external {
        string memory envName = vm.envString("CONTRACTS_ENV_NAME");
        string memory fileNames = string.concat(envName, ".json");
        fullDeploymentsPath = string.concat(vm.projectRoot(), DEPLOYMENTS_PATH, fileNames);
    }

    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(deployerPrivateKey);

        bytes memory args = abi.encode("UnstoppableModelErc20", "UMC", 18);
        UnstoppableModelErc20 token = UnstoppableModelErc20(_deployContract("UnstoppableModelErc20", "UnstoppableModelErc20", args));

        // TODO: add link
        string memory dataURI = "https:data";
        string memory modelDataURL = "QmdUaWbsFep3iVjMeye1o6KaBjt4nzAbEKJQM8egJRNy1y";
        UnstoppableModel unstoppableModelContract = UnstoppableModel(_deployContract("UnstoppableModel", "UnstoppableModel", abi.encode(dataURI, modelDataURL)));

        _printDeployments();
        _saveDeployment(fullDeploymentsPath);

//        // TODO: comment: do some debug staff from here.
//        TODO: move to separate script for local dev.
//        uint collateralPerLearningPeriod = unstoppableModelContract.collateralPerLearningPeriod();
//        uint256 currentTime = block.timestamp;
//        unstoppableModelContract.applyToLearnPeriod{value: collateralPerLearningPeriod}(currentTime);
//        unstoppableModelContract.submitState("QmZRLQqeazAjcu3PMdJstq2hN1vC8oMrEMBS3eGiHcnP5E");
//
//        unstoppableModelContract.suspectState{value: collateralPerLearningPeriod}(1);
//        unstoppableModelContract.reviewSuspect(1, true);
//
//        unstoppableModelContract.applyToLearnPeriod{value: collateralPerLearningPeriod}(currentTime);
//        unstoppableModelContract.submitState("QmZPLDcxYVxwTwpKU36xmmJ6kiFiVL5BqWjf6K5bWfLD8n");
//        unstoppableModelContract.submitState("QmW3Tar6cPjufwkgAfZrfsRRWM7RJSqCxiRJNPfv6X54Uy");

        vm.stopBroadcast();
    }
}

