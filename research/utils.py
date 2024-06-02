import streamlit as st
import pandas as pd
import numpy as np

import numpy as np
import pandas as pd
import torch

import os

import time

from sklearn.datasets import load_iris

import matplotlib.pyplot as plt
from IPython.display import display, clear_output

from subgrounds import Subgrounds
import ipfs_api


DEFAULT_SUBGRAPH_PATH = "http://localhost:8000/subgraphs/name/unstoppable-models"
STATE_IS_DELETED = "modelStates_deleted"
STATE_MODEL_IPFS = "modelStates_url"
STATE_BS_TIME = "modelStates_submittedAt"
DATA_DIR = "data"

def read_all_good_states_links():
    sg = Subgrounds()
    sub = sg.load_subgraph(DEFAULT_SUBGRAPH_PATH)
    states = sg.query_df(sub.Query.modelStates())
    good_states = []
    good_states = []
    for s in states[[STATE_IS_DELETED, STATE_BS_TIME, STATE_MODEL_IPFS]].values:
        is_deleted, ts, model_path = s
        if is_deleted:
            continue
        good_states.append((ts, model_path))
    good_states = sorted(good_states, key=lambda x: x[0])
    return [x[1] for x in good_states]


def get_all_good_models_params():
    states = read_all_good_states_links()
    assert len(states) > 0
    state_dicts = []
    for s in states:
        ipfs_hash = s.split("/")[-1]
        assert ipfs_hash[0] == "Q"
        ipfs_api.http_client.get(ipfs_hash, DATA_DIR)
        state_dict = torch.load(os.path.join(DATA_DIR, ipfs_hash))
        state_dicts.append(state_dict)
    return state_dicts
        


class Task:
    def __init__(self, X, y, batch_size, model_fn):
        self.X = X
        self.y = y
        self.batch_size = batch_size
        self.state = 0
        self.total_batches = len(self.X) // batch_size
        self.model_fn = model_fn
        model = self.model_fn()
        self.model_weights = [model.state_dict(),]
        self.losses = [self.calc_global_loss(model).item()]

    def batch(self, state=-1):
        if state == -1:
            state = self.state
        batch = self.state % self.total_batches
        begin = batch * self.batch_size
        end = (batch + 1) * self.batch_size
        return self.X[begin:end], self.y[begin:end]
    
    def submit_update(self, weights, loss):
        self.state += 1
        self.model_weights.append(weights)
        self.losses.append(loss)

    def set_state(self, state):
        self.state = state
        self.model_weigthts = self.model_weights[:self.state + 1]
        self.losses = self.losses[:self.state + 1]
    
    def model(self, state=-1):
        model = self.model_fn() 
        model.load_state_dict(self.model_weights[state])
        return model


    def calc_global_loss(self, model):
        model.train(False)
        y_pred_global = model(self.X)
        loss_global = criterion(y_pred_global, self.y)
        return loss_global


model_fn = lambda: torch.nn.Sequential(
    torch.nn.Linear(4, 8),
    torch.nn.ReLU(),
    torch.nn.Linear(8, 4))

def get_dataset():
    X, y = load_iris(return_X_y=True)
    np.random.seed(0)
    idx = np.arange(len(X))
    np.random.shuffle(idx)  
    Xt = torch.Tensor(X[idx])
    yt = torch.LongTensor(y[idx]).reshape(-1,1)
    return Xt, yt

def get_default_task():
    Xt, yt = get_dataset()
    task = Task(Xt, yt, batch_size=32, model_fn=model_fn)
    return task


def criterion(logits, labels):
    log_softmax = torch.nn.LogSoftmax(dim=1)(logits)
    batch_size = logits.shape[0]
    batch_idx = torch.arange(batch_size).unsqueeze(1)
    return -torch.mean(log_softmax[batch_idx, labels.reshape(-1)])


def compare(model, other_model):
    for t, tt in zip(model.parameters(), other_model.parameters()):
        if not torch.allclose(t, tt, 1e-5):
            return False
    return True

def get_algorithm(model):
    return torch.optim.SGD(model.parameters(), lr=0.01)
        