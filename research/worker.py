import torch
import os
import time

from utils import Task, model_fn, get_dataset, criterion, compare, get_default_task, get_all_good_models_params, get_algorithm
from web3_utils import call_contract
import ipfs_api

WEIGHTS_DIR = "weights"
    

def submit_weights(i, weights):
    path = os.path.join(WEIGHTS_DIR, str(i) + ".pth")
    torch.save(weights, path)
    r = ipfs_api.http_client.add(path)
    ipfs_hash = r.as_json()["Hash"]
    print(call_contract("submitState", ipfs_hash))


def apply_to_learn_period():
    print(call_contract("applyToLearnPeriod", int(time.time()), 1000000000000000))


def main():
    task = get_default_task()
    current_state_id = -1
    while True:
        all_good_states_models = get_all_good_models_params()
        new_current_state_id = len(all_good_states_models) - 1
        print("Current state id & next", current_state_id, new_current_state_id)
        current_state_weights = all_good_states_models[-1]
        if new_current_state_id == current_state_id:
            print("Got current state, sleep")
            time.sleep(5)
            continue
        else:
            print("Advance current state")
            current_state_id = new_current_state_id
        apply_to_learn_period()
        model = model_fn()
        model.load_state_dict(current_state_weights)
        print("Before " + str(task.calc_global_loss(model).item()))
        model.train(True)
        X, y = task.batch(current_state_id)
        y_pred = model(X)
        # if malicious:
        #     y_batch = torch.zeros_like(y_batch)
        loss = criterion(y_pred, y)
        optimizer = get_algorithm(model)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        print("After " + str(task.calc_global_loss(model).item()))
        weights = model.state_dict()
        submit_weights(current_state_id, weights)

main()