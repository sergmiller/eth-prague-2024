// SPDX-License-Identifier: UNLICENSED
pragma solidity >=0.8.10;

import "solmate/tokens/ERC721.sol";
import "openzeppelin-contracts/contracts/utils/Strings.sol";
import "openzeppelin-contracts/contracts/access/Ownable.sol";

// TODO: add custom errors below.
error WithdrawError();

// 1 Contract - 1 Model
// TODO: apply Factory model to this contract.
// This Contract should be controlled by DAO/multisig aka by validators DAO.
contract UnstoppableModel is Ownable {
    using Strings for uint256;
    // Uploaded to IPFS Model data.
    string public modelDataURL;
    // Only owner could change the this.
    uint256 public expectedStatesPerPeriod = 1;
    uint256 public stateLearningSecondsMax = 100;
    // After the end period fraud proofer has some time to suspect.
    uint256 public availableToSuspectSeconds = 100;
    // TODO: use different collateral per suspect and period apply.
    uint256 public collateralPerLearningPeriod = 0.001 ether;

    event ApplyToLearnPeriod(address indexed worker, uint256 start, uint256 end, uint256 expectedStates);
    event SubmitState(uint256 indexed learningPeriodId, string url, uint256 submittedAt);
    event WithdrawCollateralPerLearningPeriod(uint256 indexed learningPeriodId, address worker);
    event SuspectState(uint256 indexed stateId, address suspectedBy, uint256 suspectedAt);

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

    LearningPeriod[] learningPeriods;
    ModelState[] modelStates;

    constructor(
        string memory modelDataURL_
    ) Ownable(msg.sender) {
        modelDataURL = modelDataURL_;
        LearningPeriod memory newLearningPeriod = LearningPeriod(
            msg.sender,
            0,
            0,
            0,
            false,
            false
        );
        learningPeriods.push(newLearningPeriod);
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

        // ApplyToLearnPeriod(address indexed worker, uint256 start, uint256 end, uint256 expectedStates);
        emit ApplyToLearnPeriod(msg.sender, start, start + expectedStatesPerPeriod * stateLearningSecondsMax, expectedStatesPerPeriod);
    }

    function submitState(string memory url_, uint256 learningPeriodId) external {
        require(learningPeriodId < learningPeriods.length, "Learning period not found.");
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
        require(currentTime > learningPeriod.end + availableToSuspectSeconds, "Not possible to withdraw now because of suspection period.");
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

        emit SuspectState(stateId, msg.sender, currentTime);
    }

    function reviewSuspect(uint256 stateId, bool isSuspectValid) external onlyOwner {
        ModelState storage suspectedState = modelStates[stateId];
        require(suspectedState.suspectedAt > 0, "State is not suspected.");

        if (isSuspectValid) {
            // Invalidate state:
            // - remove the state and all states after.
            // - Clean learning periods registered after.
            // - reward suspecter.
            for (uint256 i = modelStates.length - 1; i >= stateId; i--) {
                ModelState memory modelState = modelStates[i];
                uint256 learningPeriodId = modelState.learningPeriodId;

                if (learningPeriodId < learningPeriods.length) {
                    LearningPeriod storage learningPeriod = learningPeriods[learningPeriodId];
                    if (learningPeriod.worker != msg.sender) {
                        msg.sender.call{value: collateralPerLearningPeriod}("");
                        // TODO: how to catch error properly for this case.
                    }
                    delete learningPeriods[learningPeriodId];
                }
                delete modelStates[i];
            }
        } else {
            LearningPeriod storage learningPeriod = learningPeriods[suspectedState.learningPeriodId];
            // Remove evidence of suspection.
            learningPeriod.anyStateSuspected = false;
            suspectedState.suspectedAt = 0;
            suspectedState.suspectedBy = address(0);
        }

//        TODO: event
    }
}
