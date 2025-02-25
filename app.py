import streamlit as st
from langchain_helper import get_few_shot_db_chain

st.title("M Bazar : Database Q&A 👕")

question = st.text_input("Enter your question:")

if question:
    try:
        chain = get_few_shot_db_chain()
        response = chain.invoke({"query": question}) 
        
        st.header("Answer")
        st.write(response)
    except Exception as e:
        st.error(f"An error occurred: {e}")
