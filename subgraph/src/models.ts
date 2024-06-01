import {
  GraphNetwork,
} from "../generated/schema";
import { Address, BigInt, Bytes } from "@graphprotocol/graph-ts";

export const ZERO_BIG_INT = BigInt.fromI32(0);
export const UNO_BIG_INT = BigInt.fromI32(1);
export const MAX_UINT_256 = BigInt.fromString(
  "115792089237316195423570985008687907853269984665640564039457584007913129639935",
);
export const ZERO_ADDRESS = "0x0000000000000000000000000000000000000000";

export function createOrLoadGraphNetwork(): GraphNetwork {
  let graphNetwork = GraphNetwork.load("1");
  if (graphNetwork == null) {
    graphNetwork = new GraphNetwork("1");
    graphNetwork.dealsTotal = ZERO_BIG_INT;
    graphNetwork.providersTotal = ZERO_BIG_INT;
    graphNetwork.providersRegisteredTotal = ZERO_BIG_INT;
    graphNetwork.offersTotal = ZERO_BIG_INT;
    graphNetwork.tokensTotal = ZERO_BIG_INT;
    graphNetwork.effectorsTotal = ZERO_BIG_INT;
    graphNetwork.capacityCommitmentsTotal = ZERO_BIG_INT;
    graphNetwork.proofsTotal = ZERO_BIG_INT;
    graphNetwork.save();
  }
  return graphNetwork as GraphNetwork;
}