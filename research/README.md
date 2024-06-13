# Start

To init project you need to prepare the first state, e.g.:

```pytohn
import ipfs_api
import torch

model_fn = lambda: torch.nn.Sequential(
    torch.nn.Linear(4, 8),
    torch.nn.ReLU(),
    torch.nn.Linear(8, 4))


model = model_fn()
torch.save(model.state_dict(), "/Users/<>/Downloads/test_state.pth")
r = ipfs_api.http_client.add("/Users/<>/Downloads/test_state.pth")
print(r.as_json()["Hash"])
```