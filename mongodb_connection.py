import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

def connect():
    password = st.secrets['password']
    username = st.secrets['username']
    uri = f"mongodb+srv://{username}:{password}@userdndinder.hf3y3.mongodb.net/?retryWrites=true&w=majority&appName=UserDnDinder"
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    return client
