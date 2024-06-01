import {
    ApplyToLearnPeriod, SubmitState, SuspectState,
    WithdrawCollateralPerLearningPeriod
} from "../../generated/UnstoppableModel/UnstoppableModel";
import {LearningPeriod, ModelState} from "../../generated/schema";
import {UNO_BIG_INT, ZERO_BIG_INT} from "../models";
import {formatAddress} from "./utils";

// event ApplyToLearnPeriod(address indexed worker, uint256 start, uint256 end, uint256 expectedStates);
export function handleApplyToLearnPeriod(event: ApplyToLearnPeriod): void {
    const _id = event.params.learningPeriodId.toHexString()
    let entity = LearningPeriod.load(_id);

    if (entity == null) {
        entity = new LearningPeriod(_id);
        entity.worker = formatAddress(event.params.worker);
        entity.start = event.params.start;
        entity.end = event.params.end;
        entity.submittedStates = ZERO_BIG_INT;
        entity.collateralWithdrawn = false
        entity.anyStateSuspected = false
        entity.deleted = false
        entity.save();
    }
}

export function handleSubmitState(event: SubmitState): void {
    let learningPeriod = LearningPeriod.load(event.params.learningPeriodId.toHexString()) as LearningPeriod

    const _id = event.params.url
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

}
export function handleWithdrawCollateralPerLearningPeriod(event: WithdrawCollateralPerLearningPeriod): void {

}