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

        unstoppableModelContract = new UnstoppableModel("linktodatafoo");
    }

    function testSetOwner() public {
        vm.prank(dev);
        vm.expectRevert();
        unstoppableModelContract.transferOwnership(dev);
    }

    function testSuccessFlow() public {
        uint256 currentTime = block.timestamp;

        unstoppableModelContract.applyToLearnPeriod(currentTime);

    }

//    function testFoo(uint256 x) public {
//        vm.assume(x < type(uint128).max);
//        assertEq(x + x, x * 2);
//    }
}
