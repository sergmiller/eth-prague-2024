// SPDX-License-Identifier: UNLICENSED
pragma solidity >=0.8.10;

import "solmate/tokens/ERC721.sol";
import "openzeppelin-contracts/contracts/utils/Strings.sol";
import "openzeppelin-contracts/contracts/access/Ownable.sol";

import "forge-std/console.sol";

// TODO: add custom errors below.
error WithdrawError();

// 1 Contract - 1 Model
// TODO: apply Factory model to this contract.
// This Contract should be controlled by DAO/multisig aka by validators DAO.
contract UnstoppableModel is Ownable {
    using Strings for uint256;
    // Uploaded to IPFS Model data.
    // TODO: use in frontend.
    string public modelDataURL;
    // Only owner could change the this.
    uint256 public expectedStatesPerPeriod = 3;
    uint256 public stateLearningSecondsMax = 100;
    // After the end period fraud proofer has some time to suspect.
    uint256 public availableToSuspectSeconds = 100;
    // TODO: use different collateral per suspect and period apply.
    uint256 public collateralPerLearningPeriod = 0.001 ether;

    event ApplyToLearnPeriod(address indexed worker, uint256 start, uint256 end, uint256 expectedStates, uint256 learningPeriodId);
    event SubmitState(uint256 indexed learningPeriodId, string url, uint256 submittedAt);
    event WithdrawCollateralPerLearningPeriod(uint256 indexed learningPeriodId, address worker);
    event SuspectState(uint256 indexed stateId, address suspectedBy, uint256 suspectedAt, string url);
//    function reviewSuspect(uint256 stateId, bool isSuspectValid) external onlyOwner {
    event ReviewSuspect(uint256 indexed stateId, bool isSuspectValid, string url);
//    TODO: event avout resolution...

    // Each future state should be better than the previous one, otherwise it is possible to suspect.
    struct ModelState {
        // Url to IPFS.
        string url;
        uint256 submittedAt;
        uint256 suspectedAt;
        address suspectedBy;
        uint256 learningPeriodId;
    }

    // TODO: when collateral withdrawn - delete from memory.
    // TODO: add expectedStates as argument
    // After state suspected -> it removed and thus all learning periods after suspected are removed.
    struct LearningPeriod {
        address worker;
        uint256 start;
        // TODO: could be removed to optim.
        uint256 end;
        // How many states were submitted.
        uint256 submittedStates;
        // When collateral withdrawn -> state accepted truly.
        bool collateralWithdrawn;
        // To decide if it is possible to withdraw collateral.
        bool anyStateSuspected;
    }

    LearningPeriod[] public learningPeriods;
    ModelState[] public modelStates;

    constructor(
        string memory modelDataURL_
    ) Ownable(msg.sender) {
        modelDataURL = modelDataURL_;
        // Every one knows initial state of the model. Or we could provide it on construct.
        LearningPeriod memory newLearningPeriod = LearningPeriod(
            msg.sender,
            0,
            0,
            0,
            false,
            false
        );
        learningPeriods.push(newLearningPeriod);
        ModelState memory modelState = ModelState("QmZG8N5mxLiNCzE8Vnvtcr7UXbSVMQnHw4oCauJzpRkPM6", 0, 0, address(0), 0);
        modelStates.push(modelState);

        emit ApplyToLearnPeriod(msg.sender, 0, 0, 1, 0);
        uint256 currentTime = block.timestamp;
        emit SubmitState(0, "QmZG8N5mxLiNCzE8Vnvtcr7UXbSVMQnHw4oCauJzpRkPM6", currentTime);
    }

    function setExpectedStatesPerPeriod(uint256 newExpectedStatesPerPeriod) external onlyOwner {
        expectedStatesPerPeriod = newExpectedStatesPerPeriod;
    }
    //    TODO: add function to change model hyper params as well (DAO could change it).

    // @dev By applying to learn period, worker should submit at least EXPECTED_STATES_PER_PERIOD states.
    //    TODO: payable.
    function applyToLearnPeriod(uint256 start) external payable {
        require(msg.value >= collateralPerLearningPeriod, "Collateral is not enough.");

        LearningPeriod memory lastLearningPeriod = learningPeriods[learningPeriods.length - 1];
        require(lastLearningPeriod.end < start, "Not possible to apply now.");

        LearningPeriod memory newLearningPeriod = LearningPeriod(
            msg.sender,
            start,
            start + expectedStatesPerPeriod * stateLearningSecondsMax,
            0,
            false,
            false
        );
        learningPeriods.push(newLearningPeriod);

        emit ApplyToLearnPeriod(msg.sender, start, start + expectedStatesPerPeriod * stateLearningSecondsMax, expectedStatesPerPeriod, learningPeriods.length - 1);
    }

    function submitState(string memory url_) external {
        uint256 learningPeriodId = learningPeriods.length - 1;
        LearningPeriod storage learningPeriod = learningPeriods[learningPeriodId];
        require(learningPeriod.worker == msg.sender, "Not your learning period.");
        require(learningPeriod.submittedStates < expectedStatesPerPeriod, "All states submitted.");

        uint256 currentTime = block.timestamp;
        ModelState memory newState = ModelState(url_, currentTime, 0, address(0), learningPeriodId);

        modelStates.push(newState);
        learningPeriod.submittedStates++;

        emit SubmitState(learningPeriodId, url_, currentTime);
    }

    // Should have not suspection and allowed time.
    function withdrawCollateralPerLearningPeriod(uint256 learningPeriodId, address withdrawTo) external {
        LearningPeriod storage learningPeriod = learningPeriods[learningPeriodId];
        require(learningPeriod.worker == msg.sender, "Not your learning period.");
        require(learningPeriod.submittedStates == expectedStatesPerPeriod, "To all states submitted.");
        require(!learningPeriod.anyStateSuspected, "State is currently suspected.");
        uint256 currentTime = block.timestamp;
//        TODO: debug.
//        require(currentTime > learningPeriod.end + availableToSuspectSeconds, "Not possible to withdraw now because of suspection period.");
        require(address(this).balance >= collateralPerLearningPeriod, "Not enough balance.");

        (bool success, ) = payable(withdrawTo).call{value: collateralPerLearningPeriod}("");
        if (!success) revert WithdrawError();

        // TODO: flush lists after withdraw.

        emit WithdrawCollateralPerLearningPeriod(learningPeriodId, msg.sender);
    }

    //    TODO: use USDC
    function suspectState(uint256 stateId) external payable {
        require(msg.value >= collateralPerLearningPeriod, "Collateral is not enough.");
        require(stateId < modelStates.length, "State not found.");

        ModelState storage suspectedState = modelStates[stateId];
        uint256 currentTime = block.timestamp;
        suspectedState.suspectedAt = block.timestamp;
        suspectedState.suspectedBy = msg.sender;

        LearningPeriod storage learningPeriod = learningPeriods[suspectedState.learningPeriodId];
        learningPeriod.anyStateSuspected = true;

        emit SuspectState(stateId, msg.sender, currentTime, suspectedState.url);
    }

    function reviewSuspect(uint256 stateId, bool isSuspectValid) external onlyOwner {
        ModelState storage suspectedState = modelStates[stateId];
        require(suspectedState.suspectedAt > 0, "State is not suspected.");
        require(stateId > 0, "The initial state could not be suspected.");

        if (isSuspectValid) {
            // Invalidate state:
            // - remove the state and all states after.
            // - Clean learning periods registered after.
            // - reward suspecter.
            for (uint256 i = modelStates.length - 1; i >= stateId; i--) {
                console.log("i: %s", i.toString());
                ModelState memory modelState = modelStates[i];
                uint256 learningPeriodId = modelState.learningPeriodId;  // 1

//                1 <? 2
                if (learningPeriodId < learningPeriods.length) {
                    LearningPeriod storage learningPeriod = learningPeriods[learningPeriodId];
                    if (learningPeriod.worker != msg.sender) {
                        address sentTo = learningPeriod.worker;
                        (bool success, ) = payable(sentTo).call{value: collateralPerLearningPeriod}("");
                        if (!success) revert WithdrawError();
                    }
                    console.log('Before delete learningPeriods[learningPeriodId]: %s', learningPeriodId);
                    delete learningPeriods[learningPeriodId];
                }
                console.log('Before delete modelStates[i]: %s', i);
                delete modelStates[i];
            }
            address sendTo = suspectedState.suspectedBy;
            (bool success, ) = payable(sendTo).call{value: collateralPerLearningPeriod}("");
            if (!success) revert WithdrawError();
        } else {
            LearningPeriod storage learningPeriod = learningPeriods[suspectedState.learningPeriodId];
            // Remove evidence of suspection.
            learningPeriod.anyStateSuspected = false;
            suspectedState.suspectedAt = 0;
            suspectedState.suspectedBy = address(0);
        }

        emit ReviewSuspect(stateId, isSuspectValid, suspectedState.url);
    }
}
