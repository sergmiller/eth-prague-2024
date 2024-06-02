// SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.13;

import "forge-std/Test.sol";

import {Utils} from "./Utils.sol";
import "src/UnstoppableModel.sol";

contract TestUnstoppableModelContract is Test {
    Utils internal utils;
    address payable[] internal users;
    address internal owner;
    address internal dev;
    UnstoppableModel internal unstoppableModelContract;

    function setUp() public {
        utils = new Utils();
        users = utils.createUsers(2);
        owner = users[0];
        vm.label(owner, "Owner");
        dev = users[1];
        vm.label(dev, "Developer");

        unstoppableModelContract = new UnstoppableModel("linktodatafoo", "linkToFooModelState0");
    }

    function testSetOwner() public {
        vm.prank(dev);
        vm.expectRevert();
        unstoppableModelContract.transferOwnership(dev);
    }

    function testSuccessFlow() public {
        uint256 currentTime = block.timestamp;

        // Impossible to send less collateral.
        uint collateralPerLearningPeriod = unstoppableModelContract.collateralPerLearningPeriod();
        vm.expectRevert();
        unstoppableModelContract.applyToLearnPeriod{value: collateralPerLearningPeriod - 1}(currentTime);

        // PeriodId == 1
        unstoppableModelContract.applyToLearnPeriod{value: collateralPerLearningPeriod}(currentTime);

        // Check: Not possible to apply for the same period.
        vm.expectRevert();
        unstoppableModelContract.applyToLearnPeriod{value: collateralPerLearningPeriod}(currentTime);

        unstoppableModelContract.setExpectedStatesPerPeriod(1);
        unstoppableModelContract.submitState("linktodatafoo1");

        vm.expectRevert();
        unstoppableModelContract.submitState("linktodatafoo2");

//        vm.expectRevert(abi.encodePacked("Not possible to withdraw now because of suspection period."));
//        unstoppableModelContract.withdrawCollateralPerLearningPeriod(1, address(0));

        uint256 stateLearningSecondsMax = unstoppableModelContract.stateLearningSecondsMax();
        uint256 expectedStatesPerPeriod = unstoppableModelContract.expectedStatesPerPeriod();
        uint availableToSuspectSeconds = unstoppableModelContract.availableToSuspectSeconds();
        StdCheats.skip(stateLearningSecondsMax * expectedStatesPerPeriod + availableToSuspectSeconds + 1);

        unstoppableModelContract.withdrawCollateralPerLearningPeriod(1, address(0));
    }

    function testSuspectFlowValid() public {
        uint256 currentTime = block.timestamp;

        // Impossible to send less collateral.
        uint collateralPerLearningPeriod = unstoppableModelContract.collateralPerLearningPeriod();

        // PeriodId == 1
        unstoppableModelContract.applyToLearnPeriod{value: collateralPerLearningPeriod}(currentTime);
        // Check that realy saved.
        (address applierAddress,,,,,) = unstoppableModelContract.learningPeriods(1);
        assertNotEq(applierAddress, address(0));

        // Check: Not possible to apply for the same period.
        vm.expectRevert();
        unstoppableModelContract.applyToLearnPeriod{value: collateralPerLearningPeriod}(currentTime);

        unstoppableModelContract.setExpectedStatesPerPeriod(1);
        unstoppableModelContract.submitState("linktodatafoo1");

        unstoppableModelContract.suspectState{value: collateralPerLearningPeriod}(1);
        unstoppableModelContract.reviewSuspect(1, true);

        // Check that learning periods are only 1 element (0).
        // Check that model states only 1 (0).
        unstoppableModelContract.modelStates(0);
        (string memory url,,,,) = unstoppableModelContract.modelStates(1);
        assertEq(url, "");

        unstoppableModelContract.learningPeriods(0);
        (address worker,,,,,) = unstoppableModelContract.learningPeriods(1);
        assertEq(worker, address(0));

        // Lets apply again and validate the index.
        unstoppableModelContract.applyToLearnPeriod{value: collateralPerLearningPeriod}(currentTime);
        (address newApplierAddress,,,,,) = unstoppableModelContract.learningPeriods(2);
        assertNotEq(newApplierAddress, address(0));
    }

//    function testFoo(uint256 x) public {
//        vm.assume(x < type(uint128).max);
//        assertEq(x + x, x * 2);
//    }
}
