# run with: python3 -m streamlit run demo.py
import streamlit as st
import pandas as pd
import numpy as np

import numpy as np
import pandas as pd
import os
import torch

import time

from sklearn.datasets import load_iris

import matplotlib.pyplot as plt

from utils import Task, model_fn, criterion, compare, get_algorithm, get_default_task, get_all_good_models_params

CONTRACT_ADDRESS = os.environ.get('CONTRACT_ADDRESS', "0x8CCF4E32f4Ab25e5b121D3e6E06379b59CB408D7")

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


def calc_losses(task):
    params = get_all_good_models_params()
    losses = []
    for i in range(len(params)):
        model = model_fn()
        model.load_state_dict(params[i])
        losses.append(task.calc_global_loss(model).item())
    return losses
        

def main():
    torch.manual_seed(42)
    task = get_default_task()
    while True:
        losses = calc_losses(task)
        print(losses)
        draw(losses)
        time.sleep(5)


# fig, ax = plt.subplots()



# clear_output(wait=True)


def stream_markdown(markdown_text):
    for word in markdown_text.split(" "):
        yield word + " "
        time.sleep(0.04)

st.header('Unstoppable AI', divider='rainbow')
overview_markdown = (
    'We aim to create a public ML model training initiative (as a public good) where anyone can freely submit the next '
    'weight update for the model according to a fixed algorithm on a fixed dataset. :sunglasses:')
st.write_stream(stream_markdown(overview_markdown))
st.link_button("View Presentation", f"https://github.com/whynft/unstoppable-models-mvp/blob/main/docs/Unstoppable%20Models.pdf")

st.header("Features")
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("Continuous Improvement", divider='rainbow')
    st.write_stream(stream_markdown("The model can only be improved, as updates are verified for correctness before being accepted"))
    # st.image("https://static.streamlit.io/examples/cat.jpg")

with col2:
    st.subheader("True Open Source", divider='rainbow')
    st.write_stream(stream_markdown("The initiative ensures that the model and its updates remain open and accessible to everyone"))

with col3:
    st.subheader("Ownership Resistance", divider='rainbow')
    st.write_stream(stream_markdown("Once an AI model is published, it cannot be regulated or stopped by any proprietary authority (unlike GPT-3)"))

st.header("Live Demo")
st.write_stream(stream_markdown(
    'Currently, to maintain protocol demo contracts were deployed on Cardona zkEVM (Polygon zkEVM testnet). :rocket: :rocket: :rocket:'
))

st.link_button("Explore Contract", f"https://cardona-zkevm.polygonscan.com/address/{CONTRACT_ADDRESS}")
st.subheader('Model Train Loss')
# scenario()

main()


# Create a line chart


