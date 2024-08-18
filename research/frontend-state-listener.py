# run with: python3 -m streamlit run demo.py
import streamlit as st
import requests
import os
import torch
import time

from utils import Task, model_fn, criterion, compare, get_algorithm, get_default_task, get_all_good_models_params

CONTRACT_ADDRESS = os.environ.get('CONTRACT_ADDRESS', "0x8CCF4E32f4Ab25e5b121D3e6E06379b59CB408D7")

def publish_task():
    global task
    torch.manual_seed(42)
    task = Task(Xt, yt, batch_size=32, model_fn=model_fn)

import altair as alt
import pandas as pd

chart = None


def draw(vals):
    global chart
    df = pd.DataFrame({'optimisation step': range(len(vals)), 'loss function': vals})

    line_chart = alt.Chart(df).mark_line(color='green').encode(
        x='optimisation step',
        y='loss function'
    )

    scatter_chart = alt.Chart(df).mark_circle(color='green').encode(
        x='optimisation step',
        y='loss function'
    )

    combined_chart = line_chart + scatter_chart

    if chart is None:
        chart = st.altair_chart(combined_chart, use_container_width=True)
    else:
        chart.altair_chart(combined_chart, use_container_width=True)
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
        time.sleep(10001)


# fig, ax = plt.subplots()



# clear_output(wait=True)


def stream_markdown(markdown_text):
    for word in markdown_text.split(" "):
        yield word + " "
        # TODO: uncomment
        # time.sleep(0.04)



st.header('Unstoppable AI', divider='rainbow')
overview_markdown = (
    'We aim to create a public ML model training initiative (as a public good) where anyone can freely submit the next '
    'weight update for the model according to a fixed algorithm on a fixed dataset. :sunglasses:')
st.write_stream(stream_markdown(overview_markdown))

# First modals.
general_col1, general_col2 = st.columns(2)

@st.dialog("Product Roadmap")
def view_roadmap_modal():
    st.title("Roadmap")

    with st.expander("Milestone 1: MVP for Production Model"):
        st.subheader("1 month")
        st.write("- Upgrade production model and initial dataset")
        st.write("- Adjust smart contracts for new model")
        st.write("- Implement comprehensive testing suite")

    with st.expander("Milestone 2: Contract Audit & Frontend Integration (1 month)"):
        st.subheader("1 month after 1st milestone")
        st.write("- Conduct third-party contract audit")
        st.write("- Develop and deploy public Python SDK")
        st.write("- Create Dockerfile for easy deployment")
        st.write("- Design Explorer UI")

    with st.expander("Milestone 3: Mainnet Deployment (1 month)"):
        st.subheader("1 month after 2nd milestone")
        st.write("- Develop decentralized backend")
        st.write("- Integrate backend with frontend")
        st.write("- Deploy frontend on custom domain")
        st.write("- Deploy contracts on testnet and mainnet")
        st.write("- Implement StreamingFast indexing for The Graph's Decentralized Network")
        st.write("- Share documentation and tutorials")


with general_col1:
    st.link_button("View Presentation", f"https://github.com/whynft/unstoppable-models-mvp/blob/main/docs/Unstoppable%20Models.pdf")

# with general_col2:
#     if st.button("View Roadmap"):
#         view_roadmap_modal()

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

col1, col2 = st.columns(2)
st.link_button("Explore Contract", f"https://cardona-zkevm.polygonscan.com/address/{CONTRACT_ADDRESS}")


st.subheader('Model Train Loss')
# Write description about if after optimisation loss does not increase submit fraud
st.write_stream(stream_markdown('If the loss doesn’t increase after optimization, it could mean the model is acting fraudulently—be the first to report it! Remember, a good model has a lower loss function, so catching errors helps improve overall performance.'))

# --- Modals. ----
new_col1, new_col2, new_col3, new_col4 = st.columns(4)

@st.dialog("Report Mallicios Update")
def report_update():
    st.write(f""
             f"The fraud-proofer system is designed to independently monitor updates within a set timeframe, "
             f"flagging any suspicious activity—such as malicious model optimisation - for Validator review.\n"
             f"If the Validator verifies the issue and confirms fraudulent behavior, the responsible Worker will be stopped."
             )
    st.subheader("Example of graph with reported malicious optimisation step")
    data = {
        'Iteration': list(range(13)),
        'Loss': [
            2.4, 2.2, 2.0, 1.8, 1.7,
            1.6, 1.65, 1.66, 1.6,
            1.55, 1.5, 1.45, 1.4],
        'Fraud_Detection': [
            None, None, None, None, 1.7,
            1.7, 1.69, 1.72, 1.74,
            None, None, None, None]
    }

    df = pd.DataFrame(data)

    # Create the Altair chart
    line_chart = alt.Chart(df).mark_line(color='green').encode(
        x='Iteration',
        y='Loss'
    )

    # Add another line for fraud detection, colored yellow
    fraud_line = alt.Chart(df).mark_line(color='red').encode(
        x='Iteration',
        y='Fraud_Detection'
    )

    # Combine the charts
    combined_chart = line_chart + fraud_line

    # Customize the chart appearance
    combined_chart = combined_chart.properties(
        title='Model Train Loss',
        # width=600,
        # height=400
    )
    # Display the chart in Streamlit
    st.altair_chart(combined_chart, use_container_width=True)
    # TODO: load from ipfs as for graph.
    update_choice = st.selectbox("Choose optimisation step to report:", [1, 2, 3, 4])
    if st.button("Submit Report"):
        # TODO: actual call of report API.
        st.session_state.report = {"update": update_choice}
        st.rerun()


@st.dialog("Become a Worker")
def become_worker():
    st.write("""
    As a Worker, you’ll contribute to AI model updates by staking on the accuracy of 
    your work. Once completed, your updates will be securely published on IPFS, 
    a high-availability CDN network accessible to everyone.

    Getting started is simple—download and launch our Python SDK, which includes all the tools 
    you need: connectors to data, previous model weights, and reinforcement learning weights.

    With our SDK, you step-by-step go through the process of fetching data, optimizing model weights, 
    and submitting your updates.
    
    We are currently in Beta testing. To join as a Worker and help advance open-source AI learning, 
    please enter your email below.
    """
    )

    input_email = st.text_input("Enter your email address below and we will contanct you.")
    if st.button("Submit"):
        if input_email:
            # Send email to telegram chat via bot.
            try:
                r = requests.post(
                    f"https://api.telegram.org/bot{os.environ.get('TELEGRRAM_BOT_TOKEN', '')}/sendMessage",
                    data={"chat_id": f"{os.environ.get('TELEGRAM_CHAT_ID', '')}", 
                    "text": f"New worker application from Unstoppable AI site: {input_email}"}
                )
                st.success("Email sent successfully!")
            except Exception:
                pass
            finally:
                st.rerun()
        else:
            st.warning("Please enter an email address before submitting.")

@st.dialog("Documentation")
def documentation_modal():
    st.write("""The documentation is still in progress.""")

with new_col1:
    if st.button("Become A Worker"):
        become_worker()

with new_col2:
    if st.button("Report Update"):
        report_update()

with new_col3:
    if st.button("Documentation"):
        st.info("The documentation is still in progress.")
        # documentation_modal()

with new_col4:
    if st.button("Download SDK"):
        st.info("SDK coming soon!")

if "report" in st.session_state:
    st.write(f"You reported update {st.session_state.report['update']}")

if "worker_email" in st.session_state:
    st.write(f"Thank you for your interest! We'll contact you at {st.session_state.worker_email}")
# scenario()

main()


# Create a line chart


