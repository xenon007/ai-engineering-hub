import re
import streamlit as st
from ollama import chat

# Set Streamlit page configuration (optional)
st.set_page_config(page_title="Ollama Streaming Chat", layout="centered")

def format_reasoning_response(thinking_content):
    """Format assistant content by removing think tags."""
    return (
        thinking_content.replace("<think>\n\n</think>", "")
        .replace("<think>", "")
        .replace("</think>", "")
    )

def main():
    """Main function to handle the chat interface and streaming responses."""
    st.markdown("## Ollama Streaming Chat")
    st.write("A minimal example of how to stream responses from the Llama3.2 model using the Ollama library and Streamlit.")

    # Display all previous messages
    for message in st.session_state["messages"]:
        # Skip system messages
        if message["role"] == "system":
            continue
        role = "user" if message["role"] == "user" else "assistant"
        with st.chat_message(role):
            if role == "assistant":
                # Extract and display thinking content if it exists
                pattern = r"<think>(.*?)</think>"
                think_match = re.search(pattern, message["content"], re.DOTALL)
                if think_match:
                    think_content = think_match.group(0)
                    response_content = message["content"].replace(think_content, "")
                    think_content = format_reasoning_response(think_content)
                    with st.expander("Thinking complete!"):
                        st.markdown(think_content)
                    st.markdown(response_content)
                else:
                    st.markdown(message["content"])
            else:
                st.markdown(message["content"])

    # Input for the user's new question or message
    if user_input := st.chat_input("Type your message here..."):
        # Append user's message to the conversation
        st.session_state["messages"].append({"role": "user", "content": user_input})
        
        # Display the user's message immediately
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Create a container for streaming the assistant's response
        with st.chat_message("assistant"):
            thinking_content = ""
            # First phase: Capture thinking content
            with st.status("Thinking...", expanded=True) as status:
                think_placeholder = st.empty()
                stream = chat(
                    model="deepseek-r1",
                    messages=st.session_state["messages"],
                    stream=True,
                )
                
                for chunk in stream:
                    content = chunk["message"]["content"] or ""
                    thinking_content += content
                    
                    if "<think>" in content:
                        continue
                    if "</think>" in content:
                        content = content.replace("</think>", "")
                        status.update(label="Thinking complete!", state="complete", expanded=False)
                        break
                    think_placeholder.markdown(format_reasoning_response(thinking_content))

            # Second phase: Display regular response
            response_placeholder = st.empty()
            response_content = ""
            for chunk in stream:
                content = chunk["message"]["content"] or ""
                response_content += content
                response_placeholder.markdown(response_content)

            # Save the complete response
            st.session_state["messages"].append(
                {"role": "assistant", "content": thinking_content + response_content}
            )

if __name__ == "__main__":
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
    main()