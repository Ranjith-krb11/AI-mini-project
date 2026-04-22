import streamlit as st
from services.ingestion import process_pdf
from services.agent import run_agent

# Page Configuration
st.set_page_config(page_title="Exam Revision Assistant", page_icon="📚", layout="centered")
st.title("📚 Exam Revision Assistant")
st.write("Upload your notes, and I'll help you study by explaining concepts, generating quizzes, or creating flashcards!")

# --- SIDEBAR: Document Upload ---
with st.sidebar:
    st.header("1. Upload Study Material")
    uploaded_file = st.file_uploader("Upload a PDF syllabus or notes", type=["pdf"])
    
    if uploaded_file and st.button("Process Document"):
        with st.spinner("Reading and storing your notes..."):
            try:
                num_chunks = process_pdf(uploaded_file)
                st.success(f"Successfully processed {uploaded_file.name} into {num_chunks} searchable chunks!")
            except Exception as e:
                st.error(f"Error processing file: {e}")
                
    # Make sure to import this at the top of app.py if you haven't already:
# from database.vector_db import get_or_create_collection

    # --- Add this inside your `with st.sidebar:` block ---
    st.divider()
    st.header("🛠️ Admin Panel")

    if st.button("View Database Contents"):
        from database.vector_db import get_or_create_collection
        
        collection = get_or_create_collection()
        total_items = collection.count()
        
        if total_items == 0:
            st.info("The database is currently empty.")
        else:
            st.success(f"Database contains {total_items} chunks.")
            
            # Fetch the data
            db_data = collection.get()
            
            # Format it into a list of dictionaries so Streamlit can display it as a table
            table_data = []
            for i in range(len(db_data['ids'])):
                table_data.append({
                    "ID": db_data['ids'][i],
                    "Source File": db_data['metadatas'][i].get('source', 'Unknown'),
                    "Text Content": db_data['documents'][i]
                })
                
            # Display as a clean, scrollable data table
            st.dataframe(table_data, use_container_width=True)

# --- MAIN CHAT INTERFACE ---
st.header("2. Study Session")

# Initialize chat history in Streamlit session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! Upload your notes on the left, then ask me to quiz you or explain a topic."}
    ]

# Display existing chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle new user input
if prompt := st.chat_input("E.g., 'Create a 3-question multiple choice quiz on chapter 1'"):
    
    # Display user message in UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Get AI response and display it
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = run_agent(prompt)
            st.markdown(response)
            
    # Save AI response to history
    st.session_state.messages.append({"role": "assistant", "content": response})