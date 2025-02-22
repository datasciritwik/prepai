import streamlit as st
from modules.llm_connector import connect_llm
from modules.result_generator import chat, CHAT_FEATURES
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate

st.set_page_config(
    page_title="qna",
    # initial_sidebar_state="collapsed"
)

# Initialize session states
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add system message at initialization
    st.session_state.messages.append({"role": "system", "content": CHAT_FEATURES})

if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory()

if "conversation" not in st.session_state:
    llm = connect_llm()
    
    # Create a prompt template that includes the system message
    template = f"""
    {CHAT_FEATURES}
    
    Current conversation:
    {{history}}
    Human: {{input}}
    Assistant:"""
    
    prompt = PromptTemplate(
        input_variables=["history", "input"],
        template=template
    )
    
    st.session_state.conversation = ConversationChain(
        llm=llm,
        memory=st.session_state.memory,
        prompt=prompt,
        verbose=True
    )

# Display chat history (skip system message in display)
for message in st.session_state.messages:
    if message["role"] != "system":  # Don't display system message
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("", show_time=True):
            try:
                # Get response using conversation chain with memory
                response = st.session_state.conversation.predict(input=prompt)
                st.markdown(response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")

# Add a button to clear conversation history
if st.sidebar.button("Clear Conversation"):
    st.session_state.messages = [{"role": "system", "content": CHAT_FEATURES}]  # Keep system message
    st.session_state.memory.clear()
    st.rerun()