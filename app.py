import os
import time
import validators
import streamlit as st
from utilities.ui_utils import display_quiz
from utilities.rag_utils import rag_answer, create_vector_db
from utilities.study_aids_utils import summarizer, smart_quiz_generator
from utilities.text_utils import text_from_pdf, chunk_text, scrap_website

# 🎓 Page Configuration

st.set_page_config(
    page_title="AI Tutor for Students",
    page_icon="🎓",
    layout="wide",
)

st.title("🎓 AI Tutor for Students")

# Setting API Keys as environment variables
with st.sidebar:

    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    os.environ['GROQ_API_KEY'] = st.text_input('Enter your "Groq API key" to use the LLM:', type='password', key = 'GROQ_KEY')


# 📂 Tabs
tabs = st.tabs(["📚 Upload & Summarize", "💬 Ask Tutor", "📝 Quiz Generator"])

# ==================== 📚 Tab 1 ====================
with tabs[0]:
    st.header("📚 Upload Your Study Material")

    upload_option = st.radio(
        "Choose input type:",
        ["📄 PDF File", "🌐 Enter an Article URL"],
        horizontal=True
    )

    if upload_option == "📄 PDF File":
        pdf_file = st.file_uploader("Upload a PDF File", type=["pdf"])

        # 📄 PDF Upload
        if pdf_file:
            try:
                with st.spinner("📖 Preparing your study material..."):
                    pdf_text = text_from_pdf(pdf_file)

                    # Reset previous session data when new material is uploaded
                    if "last_pdf" not in st.session_state or st.session_state.last_pdf != pdf_file.name:
                        for key in ["pdf_summary", "pdf_vectors", "pdf_summary_time"]:
                            st.session_state.pop(key, None)
                        st.session_state.last_pdf = pdf_file.name

                    st.session_state.pdf_chunks = chunk_text(pdf_text)
                    
                    # Auto-embed for better results
                    if "pdf_vectors" not in st.session_state:
                        st.session_state.pdf_vectors = create_vector_db(st.session_state.pdf_chunks)
                
                st.success(f"✅ Material prepared: {pdf_file.name}")

                # Summarize Button
                summarize_clicked = st.button("Summarize Content")
                summary_placeholder = st.empty()

                if summarize_clicked:
                    start_time = time.process_time()
                    combined_text = "\n".join(st.session_state.pdf_chunks)
                    st.session_state.pdf_summary = summarizer(combined_text)

                    end_time = time.process_time()
                    st.session_state.pdf_summary_time = end_time - start_time

                    st.success("✅ Summary generated!")
                    st.rerun()

                # Displaying Summary
                with summary_placeholder:
                    if "pdf_summary" in st.session_state:
                        with st.expander("🧾 View PDF Summary", expanded = True):
                            st.write(st.session_state.pdf_summary)
                            st.caption(f"🕒 Time Taken: {st.session_state.pdf_summary_time:.2f} seconds")

            except Exception as e:
                st.error(f"❌ Error reading or processing the file: {e}")


    # 🌐 URL Upload
    else:
        url = st.text_input("Paste an Article URL:")

        if url and validators.url(url):
            try:
                with st.spinner("📖 Preparing your study material..."):

                    # Reset previous session data when new URL is entered
                    if "last_url" not in st.session_state or st.session_state.last_url != url:
                        for key in ["url_summary", "url_vectors", "url_summary_time"]:
                            st.session_state.pop(key, None)
                            
                        st.session_state.last_url = url

                        url_data = scrap_website(url)
                        st.session_state.url_chunks = chunk_text(url_data, chunk_size=600, chunk_overlap=100)
                    
                    # Auto-embed for better results
                    if "url_vectors" not in st.session_state:
                        st.session_state.url_vectors = create_vector_db(st.session_state.url_chunks)
                
                st.success("✅ Material prepared successfully!")

                # Summarize Button
                summarize_clicked = st.button("Summarize Content")
                summary_placeholder = st.empty()

                if summarize_clicked:
                    start_time = time.process_time()
                    combined_text = "\n".join(st.session_state.url_chunks)
                    st.session_state.url_summary = summarizer(combined_text)

                    end_time = time.process_time()
                    st.session_state.url_summary_time = end_time - start_time

                    st.success("✅ Summary generated!")
                    st.rerun()

                # Displaying Summary
                with summary_placeholder:
                    if "url_summary" in st.session_state:
                        with st.expander("🧾 View URL Summary", expanded = True):
                            st.write(st.session_state.url_summary)
                            st.caption(f"🕒 Time Taken: {st.session_state.url_summary_time:.2f} seconds")

            except Exception as e:
                st.error(f"❌ Error reading or processing file: {e}")

# ==================== 💬 Tab 2 ====================
with tabs[1]:

    st.header("💬 Ask Your AI Tutor")

    if "memory" not in st.session_state:
        st.session_state.memory = None

    source_choice = st.radio(
        "What do you want your tutor to help you with?",
        ["🌍 Search the Web", "📘 PDF File", "🔗 URL Article"],
        horizontal=True
    )

    with st.form("question_form"):
        user_query = st.text_input("💭 Type your question here:")
        submitted = st.form_submit_button("🔍 Get Answer")

        if submitted and user_query:
            try:
                with st.spinner("Thinking..."):

                    start_time = time.process_time()
                    memory = st.session_state.memory

                    # PDF Section
                    if source_choice == "📘 PDF File":
                        chunks = st.session_state.get("pdf_chunks")
                        summaries = st.session_state.get("pdf_summary")
                        vectors = st.session_state.get("pdf_vectors")

                        if not chunks:
                            st.warning("⚠️ No uploaded PDF materials found. Searching the web instead...")
                            st.session_state.tutor_ans, memory = rag_answer(query=user_query, memory=memory)
                            st.session_state.tutor_source = "Web Search"

                        elif vectors:
                            st.session_state.tutor_ans, memory = rag_answer(query=user_query, vector_db=vectors, memory=memory)
                            st.session_state.tutor_source = "PDF File"

                        elif summaries:
                            st.session_state.tutor_ans, memory = rag_answer(query=user_query, summaries=summaries, memory=memory)
                            st.session_state.tutor_source = "PDF File"

                        else:
                            st.session_state.tutor_ans, memory = rag_answer(query=user_query, chunks=chunks, memory=memory)
                            st.session_state.tutor_source = "PDF File"


                    # URL Section
                    elif source_choice == "🔗 URL Article":
                        chunks = st.session_state.get("url_chunks")
                        summaries = st.session_state.get("url_summary")
                        vectors = st.session_state.get("url_vectors")

                        if not chunks:
                            st.warning("⚠️ No uploaded URL article found. Searching the web instead...")
                            st.session_state.tutor_ans, memory = rag_answer(query=user_query, memory=memory)
                            st.session_state.tutor_source = "Web Search"

                        elif vectors:
                            st.session_state.tutor_ans, memory = rag_answer(query=user_query, vector_db=vectors, memory=memory)
                            st.session_state.tutor_source = "URL Article"

                        elif summaries:
                            st.session_state.tutor_ans, memory = rag_answer(query=user_query, summaries=summaries, memory=memory)
                            st.session_state.tutor_source = "URL Article"

                        else:
                            st.session_state.tutor_ans, memory = rag_answer(query=user_query, chunks=chunks, memory=memory)
                            st.session_state.tutor_source = "URL Article"


                    # Web Only
                    else:
                        st.session_state.tutor_ans, memory = rag_answer(query=user_query, memory=memory)
                        st.session_state.tutor_source = "Web Search"

                    st.session_state.memory = memory
                    end_time = time.process_time()
                    st.session_state.tutor_time = end_time - start_time
                    st.session_state.tutor_question = user_query

                    st.success("✅ Answer generated!")
                    st.rerun()

            except Exception as e:
                st.error(f"❌ Error generating answer: {e}")

    if "tutor_ans" in st.session_state and st.session_state.tutor_ans:
        with st.expander("💬 View Tutor Answer", expanded=True):

            st.markdown(f"**❓ Question:** {st.session_state.tutor_question}")
            st.write(st.session_state.tutor_ans)

            st.caption(f"🕒 Time Taken: {st.session_state.tutor_time:.2f} seconds")
            st.caption(f"📘 Source Used: {st.session_state.tutor_source}")

# ==================== 📝 Tab 3 ====================
with tabs[2]:

    st.header("📝 Quiz Generator")

    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}

    default_index = 0

    if "last_quiz_source" in st.session_state:
        mapping = {"web": 0, "pdf": 1, "url": 2}
        default_index = mapping.get(st.session_state.last_quiz_source, 0)
    else:
        if "pdf_quiz" in st.session_state:
            default_index = 1
        elif "url_quiz" in st.session_state:
            default_index = 2
        else:
            default_index = 0

    quiz_source = st.radio(
        "Select quiz source:",
        ["🌍 From the Web", "📘 From My PDF File", "🔗 From My URL Article"],
        index=default_index,
        horizontal=True
    )

    difficulty = st.select_slider(
        "Select difficulty level:",
        options=["Easy", "Medium", "Hard"],
        value="Medium"
    )

    col1, col2 = st.columns(2)
    with col1:
        num_mcq = st.number_input("Number of Multiple Choice Questions (MCQ):", min_value=1, max_value=20, value=4)

    with col2:
        num_tf = st.number_input("Number of True/False Questions:", min_value=1, max_value=20, value=3)

    topic = None

    if quiz_source == "🌍 From the Web":
        topic = st.text_input("Enter a topic:", placeholder="e.g., Neural Networks, 5G Communication, Data Structures...")

    if st.button("⚙️ Generate a Quiz"):
        try:
            with st.spinner("🧩 Generating a quiz... This might take a while"):
                
                current_prefix = ""

                if quiz_source == "🌍 From the Web":
                    current_prefix = "web"

                elif quiz_source == "📘 From My PDF File":
                    current_prefix = "pdf" 
                    
                elif quiz_source == "🔗 From My URL Article":
                    current_prefix = "url"
                
                # Remove only answers for the current quiz prefix
                keys_to_remove = [key for key in st.session_state.user_answers.keys() if key.startswith(current_prefix)]
                for key in keys_to_remove:
                    del st.session_state.user_answers[key]

                if quiz_source == "🌍 From the Web":
                    if not topic:
                        st.warning("⚠️ Please enter a topic for the web quiz.")
                        st.stop()

                    st.session_state.web_quiz = smart_quiz_generator(
                        topic_title=topic,
                        difficulty=difficulty,
                        mcq_count=num_mcq,
                        tf_count=num_tf,
                    )
                    st.success("✅ Web quiz generated successfully!")
                    st.session_state.last_quiz_source = "web"

                elif quiz_source == "📘 From My PDF File":
                    chunks = st.session_state.get("pdf_chunks")
                    if not chunks:
                        st.warning("⚠️ Please add your PDF material first.")
                        st.stop()

                    st.session_state.pdf_quiz = smart_quiz_generator(
                        difficulty=difficulty,
                        mcq_count=num_mcq,
                        tf_count=num_tf,
                        vector_db=st.session_state.get("pdf_vectors"),
                        summary=st.session_state.get("pdf_summary"),
                        chunks=chunks
                    )
                    st.success("✅ PDF quiz generated successfully!")
                    st.session_state.last_quiz_source = "pdf"

                elif quiz_source == "🔗 From My URL Article":
                    chunks = st.session_state.get("url_chunks")
                    if not chunks:
                        st.warning("⚠️ Please add your URL article first.")
                        st.stop()

                    st.session_state.url_quiz = smart_quiz_generator(
                        difficulty=difficulty,
                        mcq_count=num_mcq,
                        tf_count=num_tf,
                        vector_db=st.session_state.get("url_vectors"),
                        summary=st.session_state.get("url_summary"),
                        chunks=chunks
                    )
                    st.success("✅ URL quiz generated successfully!")
                    st.session_state.last_quiz_source = "url"

        except Exception as e:
            st.error(f"❌ Error generating quiz: {e}")

    # Display Quizzes
    if quiz_source == "🌍 From the Web" and "web_quiz" in st.session_state:
        display_quiz(st.session_state.web_quiz, "web")

    elif quiz_source == "📘 From My PDF File" and "pdf_quiz" in st.session_state:
        display_quiz(st.session_state.pdf_quiz, "pdf")

    elif quiz_source == "🔗 From My URL Article" and "url_quiz" in st.session_state:
        display_quiz(st.session_state.url_quiz, "url")