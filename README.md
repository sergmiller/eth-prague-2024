#  Unstoppable models 
(ETHPrague2024 project)

### Brief Description

We aim to create a public ML model training initiative (as a public good) where anyone can freely submit the next weight update for the model according to a fixed algorithm on a fixed dataset.

### Detailed Description

The initial weights $\theta_0$ for the model $f$ are publicly initialized offchain.

A public dataset D is fixed offchain.

In each iteration $i$, all participants are informed about the specific data chunk (batch) $D_i$ to be fed into the model to update its weights.

All interested participants locally compute gradients $\nabla_{\theta_i} f := \frac { \partial f(D_i, \theta_i) } {\partial \theta_i}$.

They submit the hash of this computation to the chain (and optionally publish the actual value publicly).

The new weights are computed as $\theta_{i+1} = \theta_i - \nu \nabla_{\theta_i} f$. (or via similar optimization algorithm)

Every k steps, the updated weights are published offchain.

### Roles

Worker - Acquires a mutex (with a deposit) and attempts to perform a weight update step (or k steps). The Worker then publishes the updated weights on IPFS.

Validator - Token holders who resolve disputes. Validators receive rewards regardless of the outcome but are incentivized to act honestly to promote project growth.

Fraud-Proofer - Independently validates selected steps within a specific timeframe and can escalate disputes to the Validator if suspicious activity is detected (posting a deposit). If a correctly identified error is confirmed by the Validator, the Fraud-Proofer receives the Worker's stake.

# Develop

## Contract

### Deploy

```bash
source .env && forge script --chain sepolia script/NFT.s.sol:MyScript --rpc-url $SEPOLIA_RPC_URL --broadcast  -vvvv --legacy
```

or to Anvil
```
forge script script/NFT.s.sol:MyScript --fork-url http://localhost:8545 --broadcast
```
