import {
    ApplyToLearnPeriod, SubmitState, SuspectState,
    WithdrawCollateralPerLearningPeriod, ReviewSuspect, LearningPeriodDeleted
} from "../../generated/UnstoppableModel/UnstoppableModel";
import {LearningPeriod, ModelState} from "../../generated/schema";
import {UNO_BIG_INT, ZERO_BIG_INT} from "../models";
import {formatAddress} from "./utils";
import { store } from "@graphprotocol/graph-ts";
import { log } from "@graphprotocol/graph-ts/index";

// event ApplyToLearnPeriod(address indexed worker, uint256 start, uint256 end, uint256 expectedStates);
export function handleApplyToLearnPeriod(event: ApplyToLearnPeriod): void {
    const _id = event.params.learningPeriodId.toHexString()
    let entity = LearningPeriod.load(_id);

    if (entity == null) {
        entity = new LearningPeriod(_id);
    }

    entity.worker = formatAddress(event.params.worker);
    entity.start = event.params.start;
    entity.end = event.params.end;
    entity.submittedStates = ZERO_BIG_INT;
    entity.collateralWithdrawn = false
    entity.anyStateSuspected = false
    entity.deleted = false
    entity.save();
}

export function handleSubmitState(event: SubmitState): void {
    let learningPeriod = LearningPeriod.load(event.params.learningPeriodId.toHexString()) as LearningPeriod

    const _id = event.params.url;
    let entity = new ModelState(_id);
    entity.url = event.params.url;
    entity.submittedAt = event.params.submittedAt;
    entity.learningPeriod = learningPeriod.id;
    entity.deleted = false
    entity.save();

    learningPeriod.submittedStates  = learningPeriod.submittedStates.plus(UNO_BIG_INT)
    learningPeriod.save()
}

export function handleSuspectState(event: SuspectState): void {
    let modelState = ModelState.load(event.params.url) as ModelState

    modelState.suspectedBy = formatAddress(event.params.suspectedBy)
    modelState.suspectedAt = event.params.suspectedAt;
    modelState.save()

    let learningPeriod = LearningPeriod.load(modelState.learningPeriod) as LearningPeriod
    learningPeriod.anyStateSuspected = true;
    learningPeriod.save()
}

export function handleWithdrawCollateralPerLearningPeriod(event: WithdrawCollateralPerLearningPeriod): void {
    let learningPeriod = LearningPeriod.load(event.params.learningPeriodId.toHexString()) as LearningPeriod
    learningPeriod.collateralWithdrawn = true;
    learningPeriod.save()
}

export function handleReviewSuspect(event: ReviewSuspect): void {
    let modelState = ModelState.load(event.params.url) as ModelState
    let learningPeriod = LearningPeriod.load(modelState.learningPeriod) as LearningPeriod
    if (event.params.isSuspectValid) {
        // Code in another handler.
    } else {
        learningPeriod.anyStateSuspected = false;
        modelState.suspectedAt = null;
        modelState.suspectedBy = null;
    }
    modelState.save()
}

export function handleLearningPeriodDeleted(event: LearningPeriodDeleted): void {
    // DELETE old one LearningPeriod.load(event.params.learningPeriodId.toHexString()) as LearningPeriod
    let learningPeriodToDelete = LearningPeriod.load(event.params.learningPeriodId.toHexString()) as LearningPeriod
    learningPeriodToDelete.deleted = true;
    learningPeriodToDelete.save()

    // let learningPeriodMarkedAsDeleted = new LearningPeriod(event.params.learningPeriodId.toHexString().concat("-deleted"));
    // learningPeriodMarkedAsDeleted.worker = learningPeriodToDelete.worker
    // learningPeriodMarkedAsDeleted.start = learningPeriodToDelete.start
    // learningPeriodMarkedAsDeleted.end = learningPeriodToDelete.end
    // learningPeriodMarkedAsDeleted.submittedStates = learningPeriodToDelete.submittedStates
    // learningPeriodMarkedAsDeleted.collateralWithdrawn = learningPeriodToDelete.collateralWithdrawn
    // learningPeriodMarkedAsDeleted.anyStateSuspected = learningPeriodToDelete.anyStateSuspected
    // learningPeriodMarkedAsDeleted.deleted = true
    // learningPeriodMarkedAsDeleted.save()

    const loadedChildModels = learningPeriodToDelete.modelStates.load()
    // Compile subgraphERROR AS100: Not implemented: Iterators
    for (let i = 0; i < loadedChildModels.length; i++) {
        log.info('TODO: Delete model stateL {}', [i.toString()])
        log.info('{}', [loadedChildModels[i].id])
        const submittedState = loadedChildModels[i];
        submittedState.deleted = true
        submittedState.save()
    }

    log.info('LearningPeriod {}', [learningPeriodToDelete.id])
    // TODO: somehow it does not work: https://github.com/graphprotocol/graph-tooling/issues/1093
    // store.remove("LearningPeriod", learningPeriodToDelete.id);
}
// handleModelStateDeleted