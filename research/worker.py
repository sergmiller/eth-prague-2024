import torch
import os
import time

from utils import Task, model_fn, get_dataset, criterion, compare, get_default_task, get_all_good_models_params
from web3_utils import call_contract

WEIGHTS_DIR = "weights"
    

def submit_weights(i, weights):
    path = os.path.join(WEIGHTS_DIR, str(i))
    torch.save(weights, path)
    r = ipfs_api.http_client.add(path)
    ipfs_hash = r.as_json()["Hash"]
    call_contract("submitState", ipfs_hash)


def apply_to_learn_period():
    call_contract("applyToLearnPeriod", int(time.time()), 1000000000000000)
 

def main():
    task = get_default_task()
    while True:
        apply_to_learn_period()
        all_good_states_models = get_all_good_models_params()
        current_state_id = len(all_good_states_models)
        current_state_weights = all_good_states_models[-1]
        model = model_fn()
        model.load_model_state(current_state_weights)
        X, y = task.state(current_state_id)
        y_pred = model(X)
        # if malicious:
        #     y_batch = torch.zeros_like(y_batch)
        loss = criterion(y_pred, y)
        optimizer = get_algorithm(model)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        weights = model.state_dict()
        submit_weights(current_state_id, weights)
        time.sleep(5)

main()