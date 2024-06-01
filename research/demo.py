# run with: python3 -m streamlit run demo.py
import streamlit as st
import pandas as pd
import numpy as np

import numpy as np
import pandas as pd
import torch

import time

from sklearn.datasets import load_iris

import matplotlib.pyplot as plt
from IPython.display import display, clear_output


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

X, y = load_iris(return_X_y=True)
np.random.seed(0)
idx = np.arange(len(X))
np.random.shuffle(idx)  
Xt = torch.Tensor(X[idx])
yt = torch.LongTensor(y[idx]).reshape(-1,1)


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


def publish_task():
    global task
    torch.manual_seed(42)
    task = Task(Xt, yt, batch_size=32, model_fn=model_fn)


chart = None
def draw(vals):
    global chart
    if chart is None:
        chart = st.line_chart(vals)
    else:
        chart.empty()
        chart.line_chart(vals)
    time.sleep(1)

def worker_make_update(i, malicious=False):
    global task
    assert i == task.state
    x_batch, y_batch = task.batch(i)
    model = task.model()
    y_pred = model(x_batch)
    y_batch_true = y_batch
    if malicious:
        y_batch = torch.zeros_like(y_batch)
    loss = criterion(y_pred, y_batch)
    optimizer = get_algorithm(model)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    weights = model.state_dict()
    loss_global = task.calc_global_loss(model)
    task.submit_update(model.state_dict(), loss_global.item())
    draw(task.losses)

def frod_proofer_suspect(i):
    pass

def validator_dao_check(i):
    global task
    model_i = task.model(i)
    model_i_next = task.model(i+1)
    x_batch, y_batch = task.batch(i)
    y_pred = model_i(x_batch)
    loss = criterion(y_pred, y_batch)
    optimizer = get_algorithm(model_i)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    is_good = compare(model_i, model_i_next)
    if not is_good:
        task.set_state(i)
    draw(task.losses)


def scenario():
    publish_task()
    for i in range(4):
        worker_make_update(i)
    worker_make_update(4)
    worker_make_update(5, malicious=True)
    worker_make_update(6)
    worker_make_update(7)
    frod_proofer_suspect(5)
    worker_make_update(8)
    validator_dao_check(5)
    worker_make_update(5)
    worker_make_update(6)
    worker_make_update(7, malicious=True)
    worker_make_update(8)
    worker_make_update(9)
    worker_make_update(10)
    frod_proofer_suspect(7)
    # validators do nothing bc of timeout for disput
    worker_make_update(11)


# fig, ax = plt.subplots()



# clear_output(wait=True)


# Set the title of the app
st.title('Model train loss')

scenario()




# Create a line chart


