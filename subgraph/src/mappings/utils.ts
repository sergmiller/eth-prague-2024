import {Address} from "@graphprotocol/graph-ts";

export function formatAddress(address: Address): string {
  return address.toHexString().toLowerCase();
}
