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
        string memory modelDataURL = "QmZG8N5mxLiNCzE8Vnvtcr7UXbSVMQnHw4oCauJzpRkPM6";
        UnstoppableModel unstoppableModelContract = UnstoppableModel(_deployContract("UnstoppableModel", "UnstoppableModel", abi.encode(dataURI, modelDataURL)));

        _printDeployments();
        _saveDeployment(fullDeploymentsPath);

        vm.stopBroadcast();
    }
}

