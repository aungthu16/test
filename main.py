import streamlit as st

st.title("My First Streamlit App")

st.write("This is a simple example of a Streamlit app.")

name = st.text_input("Enter your name:")

if st.button("Submit"):
  st.write(f"Hello, {name}!")

