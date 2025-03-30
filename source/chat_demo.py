import time
import time
import streamlit as st
import datetime


if "chat_log" not in st.session_state:
    st.session_state.chat_log = {"anna: 27.03.25 15.57.07":"Hello Bob",
                                "bob: 27.03.25 15.58.07":"Hello Anna"}

st.set_page_config(page_title="Demo")

chat_con = st.container(border=True, height=500)

for x in st.session_state.chat_log:
    if "bob" == x.split(":")[0]:
        with chat_con.chat_message(avatar="human",name=x):
            chat_con.caption(x)
            chat_con.write(st.session_state.chat_log[x])
    elif "anna" == x.split(":")[0]:
        with chat_con.chat_message(avatar="ai",name=x):
            chat_con.caption(x)
            chat_con.write(st.session_state.chat_log[x])

chat_input = st.chat_input(key="chat_input")

if not chat_input is None:
    st.session_state.chat_log["bob: " + datetime.datetime.today().strftime("%d.%m.%Y %H.%M.%S")] = chat_input
    st.rerun()
