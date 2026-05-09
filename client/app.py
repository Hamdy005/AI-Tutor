import os
import sys
import time
import validators
import streamlit as st
from supabase import create_client

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from client.ui_utils import display_quiz
from src.config import settings
from src.database import get_supabase
from src.dependencies import DEV_USER_ID
from src.store import (
    create_material, update_material_status, save_chunks,
    save_summary, save_quiz, get_material, get_chunks, get_summary,
)
from src.rag.rag import rag_answer, store_embeddings
from src.summary_generator.summary import summarizer
from src.quiz_generator.quiz import smart_quiz_generator
from src.materials.text_utils import text_from_pdf, chunk_text, scrap_website

st.set_page_config(page_title="AI Tutor", page_icon="🎓", layout="wide")


def _get_supabase_auth_client():
    if "supabase_auth_client" in st.session_state:
        return st.session_state.supabase_auth_client
    if not settings.supabase_url:
        return None
    key = settings.supabase_anon_key or settings.supabase_key
    if not key:
        return None
    client = create_client(settings.supabase_url, key)
    st.session_state.supabase_auth_client = client
    return client


def _get_query_params():
    try:
        return st.query_params
    except Exception:
        return st.experimental_get_query_params()


def _get_query_param(params, key):
    value = params.get(key)
    if isinstance(value, list):
        return value[0] if value else None
    return value


def _clear_query_params():
    try:
        st.query_params.clear()
    except Exception:
        st.experimental_set_query_params()

# ─────────────────────── AUTH ───────────────────────

if "user" not in st.session_state:
    st.title("🎓 AI Tutor — Login")

    auth_client = _get_supabase_auth_client()
    has_supabase = auth_client is not None

    if has_supabase:
        params = _get_query_params()
        auth_code = _get_query_param(params, "code")
        auth_error = _get_query_param(params, "error_description") or _get_query_param(
            params, "error"
        )
        redirect_to = os.getenv("SUPABASE_REDIRECT_URL", "")

        if auth_error:
            st.error(f"OAuth error: {auth_error}")
            _clear_query_params()
        elif auth_code:
            try:
                exchange_params = {"auth_code": auth_code}
                if redirect_to:
                    exchange_params["redirect_to"] = redirect_to
                resp = auth_client.auth.exchange_code_for_session(exchange_params)
                user = resp.user or (resp.session.user if resp.session else None)
                if not user:
                    raise ValueError("No user returned from OAuth exchange.")
                st.session_state.user = user
                _clear_query_params()
                st.rerun()
            except Exception as e:
                st.error(f"Google sign-in failed: {e}")

        tab1, tab2 = st.tabs(["Login", "Sign Up"])

        with tab1:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login"):
                try:
                    resp = auth_client.auth.sign_in_with_password(
                        {"email": email, "password": password}
                    )
                    st.session_state.user = resp.user
                    st.rerun()
                except Exception as e:
                    st.error(f"Login failed: {e}")

            st.divider()
            st.markdown("**Or continue with**")
            if not auth_code:
                try:
                    oauth_params = {"provider": "google"}
                    if redirect_to:
                        oauth_params["options"] = {"redirect_to": redirect_to}
                    oauth_resp = auth_client.auth.sign_in_with_oauth(oauth_params)
                    st.link_button("Continue with Google", oauth_resp.url)
                except Exception as e:
                    st.error(f"Google auth unavailable: {e}")

        with tab2:
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_pass")
            if st.button("Sign Up"):
                try:
                    resp = auth_client.auth.sign_up(
                        {"email": email, "password": password}
                    )
                    st.success("Check your email to confirm your account!")
                except Exception as e:
                    st.error(f"Sign up failed: {e}")
    else:
        st.info("Supabase not configured. Using dev mode.")
        email = st.text_input("Email (dev mode)")
        if st.button("Enter Dev Mode"):
            st.session_state.user = type("DevUser", (), {
                "id": DEV_USER_ID,
                "email": email or "dev@test.com",
            })()
            st.rerun()

    st.info(f"OpenRouter model: `{settings.model_name}`")
    st.stop()

# ─────────────────────── USER SETUP ───────────────────────

user_id = st.session_state.user.id
user_email = getattr(st.session_state.user, "email", "dev")

with st.sidebar:
    st.markdown(f"**Logged in:** {user_email}")
    if st.button("Logout"):
        auth_client = _get_supabase_auth_client()
        if auth_client:
            auth_client.auth.sign_out()
        for key in ["user", "memory", "pdf_chunks", "url_chunks",
                     "pdf_summary", "url_summary", "web_quiz", "pdf_quiz", "url_quiz",
                     "user_answers", "supabase_auth_client"]:
            st.session_state.pop(key, None)
        st.rerun()

st.title("🎓 AI Tutor for Students")

# ─────────────────────── TABS ───────────────────────

tabs = st.tabs(["📚 Upload & Summarize", "💬 Ask Tutor", "📝 Quiz Generator"])

# ════════════════════ TAB 1 ════════════════════
with tabs[0]:
    st.header("📚 Upload Your Study Material")

    upload_option = st.radio(
        "Choose input type:",
        ["📄 PDF File", "🌐 Enter an Article URL"],
        horizontal=True,
    )

    if upload_option == "📄 PDF File":
        pdf_file = st.file_uploader("Upload a PDF File", type=["pdf"])

        if pdf_file:
            try:
                with st.spinner("📖 Preparing your study material..."):
                    raw = text_from_pdf(pdf_file)
                    chunks = chunk_text(raw)

                    if "last_pdf" not in st.session_state or st.session_state.last_pdf != pdf_file.name:
                        for k in ["pdf_summary", "pdf_material_id", "pdf_summary_time"]:
                            st.session_state.pop(k, None)
                        st.session_state.last_pdf = pdf_file.name

                    st.session_state.pdf_chunks = chunks

                    mat = create_material(
                        user_id=user_id, source_type="pdf", title=pdf_file.name
                    )
                    mid = mat["id"]
                    chunk_ids = save_chunks(mid, chunks)
                    update_material_status(mid, "processing")
                    store_embeddings(mid, chunk_ids, chunks)
                    update_material_status(mid, "ready")
                    st.session_state.pdf_material_id = mid

                st.success(f"✅ Material prepared: {pdf_file.name}")

                if st.button("Summarize Content"):
                    start = time.time()
                    summary = summarizer("\n".join(chunks))
                    elapsed = time.time() - start

                    save_summary(mid, user_id, summary, elapsed, settings.model_name)
                    st.session_state.pdf_summary = summary
                    st.session_state.pdf_summary_time = elapsed
                    st.rerun()

                if "pdf_summary" in st.session_state:
                    with st.expander("🧾 View PDF Summary", expanded=True):
                        st.write(st.session_state.pdf_summary)
                        st.caption(f"🕒 Time: {st.session_state.pdf_summary_time:.2f}s")

            except Exception as e:
                st.error(f"❌ {e}")

    else:
        url = st.text_input("Paste an Article URL:")

        if url and validators.url(url):
            try:
                with st.spinner("📖 Preparing..."):
                    raw = scrap_website(url)
                    chunks = chunk_text(raw, chunk_size=600, chunk_overlap=100)

                    if "last_url" not in st.session_state or st.session_state.last_url != url:
                        for k in ["url_summary", "url_material_id", "url_summary_time"]:
                            st.session_state.pop(k, None)
                        st.session_state.last_url = url

                    st.session_state.url_chunks = chunks

                    mat = create_material(
                        user_id=user_id, source_type="url", title=url, url=url
                    )
                    mid = mat["id"]
                    chunk_ids = save_chunks(mid, chunks)
                    update_material_status(mid, "processing")
                    store_embeddings(mid, chunk_ids, chunks)
                    update_material_status(mid, "ready")
                    st.session_state.url_material_id = mid

                st.success("✅ Material prepared!")

                if st.button("Summarize Content"):
                    start = time.time()
                    summary = summarizer("\n".join(chunks))
                    elapsed = time.time() - start

                    save_summary(mid, user_id, summary, elapsed, settings.model_name)
                    st.session_state.url_summary = summary
                    st.session_state.url_summary_time = elapsed
                    st.rerun()

                if "url_summary" in st.session_state:
                    with st.expander("🧾 View URL Summary", expanded=True):
                        st.write(st.session_state.url_summary)
                        st.caption(f"🕒 Time: {st.session_state.url_summary_time:.2f}s")

            except Exception as e:
                st.error(f"❌ {e}")

# ════════════════════ TAB 2 ════════════════════
with tabs[1]:
    st.header("💬 Ask Your AI Tutor")

    if "memory" not in st.session_state:
        st.session_state.memory = None

    source_choice = st.radio(
        "Source:",
        ["🌍 Search the Web", "📘 PDF File", "🔗 URL Article"],
        horizontal=True,
    )

    with st.form("question_form"):
        query = st.text_input("💭 Type your question here:")
        submitted = st.form_submit_button("🔍 Get Answer")

        if submitted and query:
            try:
                with st.spinner("Thinking..."):
                    memory = st.session_state.memory
                    start = time.time()

                    if source_choice == "📘 PDF File":
                        mid = st.session_state.get("pdf_material_id")
                        chunks = st.session_state.get("pdf_chunks")
                        summary = st.session_state.get("pdf_summary")

                        if not chunks:
                            st.warning("No PDF found. Searching web...")
                            ans, memory = rag_answer(query=query, memory=memory)
                            src = "Web Search"
                        else:
                            mat = get_material(mid) if mid else None
                            if mat and mat.get("status") == "ready":
                                ans, memory = rag_answer(
                                    query=query, material_id=mid, memory=memory
                                )
                                src = "PDF (embeddings)"
                            elif summary:
                                ans, memory = rag_answer(
                                    query=query, summaries=summary, memory=memory
                                )
                                src = "PDF (summary)"
                            else:
                                ans, memory = rag_answer(
                                    query=query, chunks=chunks, memory=memory
                                )
                                src = "PDF (chunks)"

                    elif source_choice == "🔗 URL Article":
                        mid = st.session_state.get("url_material_id")
                        chunks = st.session_state.get("url_chunks")
                        summary = st.session_state.get("url_summary")

                        if not chunks:
                            st.warning("No URL found. Searching web...")
                            ans, memory = rag_answer(query=query, memory=memory)
                            src = "Web Search"
                        else:
                            mat = get_material(mid) if mid else None
                            if mat and mat.get("status") == "ready":
                                ans, memory = rag_answer(
                                    query=query, material_id=mid, memory=memory
                                )
                                src = "URL (embeddings)"
                            elif summary:
                                ans, memory = rag_answer(
                                    query=query, summaries=summary, memory=memory
                                )
                                src = "URL (summary)"
                            else:
                                ans, memory = rag_answer(
                                    query=query, chunks=chunks, memory=memory
                                )
                                src = "URL (chunks)"

                    else:
                        ans, memory = rag_answer(query=query, memory=memory)
                        src = "Web Search"

                    st.session_state.memory = memory
                    st.session_state.tutor_ans = ans
                    st.session_state.tutor_source = src
                    st.session_state.tutor_time = time.time() - start
                    st.session_state.tutor_question = query
                    st.rerun()

            except Exception as e:
                st.error(f"❌ {e}")

    if "tutor_ans" in st.session_state:
        with st.expander("💬 Answer", expanded=True):
            st.markdown(f"**Q:** {st.session_state.tutor_question}")
            st.write(st.session_state.tutor_ans)
            st.caption(f"🕒 {st.session_state.tutor_time:.2f}s — 📘 {st.session_state.tutor_source}")

# ════════════════════ TAB 3 ════════════════════
with tabs[2]:
    st.header("📝 Quiz Generator")

    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}

    quiz_source = st.radio(
        "Quiz source:",
        ["🌍 From the Web", "📘 From My PDF File", "🔗 From My URL Article"],
        horizontal=True,
    )

    difficulty = st.select_slider(
        "Difficulty:", options=["Easy", "Medium", "Hard"], value="Medium"
    )

    col1, col2 = st.columns(2)
    with col1:
        num_mcq = st.number_input("MCQ:", min_value=1, max_value=20, value=4)
    with col2:
        num_tf = st.number_input("True/False:", min_value=1, max_value=20, value=3)

    topic = None
    if quiz_source == "🌍 From the Web":
        topic = st.text_input("Topic:", placeholder="e.g. Neural Networks")

    if st.button("⚙️ Generate Quiz"):
        try:
            with st.spinner("🧩 Generating..."):
                prefix = {"🌍 From the Web": "web", "📘 From My PDF File": "pdf", "🔗 From My URL Article": "url"}[quiz_source]

                keys = [k for k in st.session_state.user_answers if k.startswith(prefix)]
                for k in keys:
                    del st.session_state.user_answers[k]

                if quiz_source == "🌍 From the Web":
                    if not topic:
                        st.warning("Enter a topic")
                        st.stop()
                    quiz = smart_quiz_generator(
                        difficulty=difficulty, mcq_count=num_mcq, tf_count=num_tf,
                        topic_title=topic,
                    )
                    save_quiz(user_id, None, "web", difficulty, num_mcq, num_tf, quiz, settings.model_name)
                    st.session_state.web_quiz = quiz

                elif quiz_source == "📘 From My PDF File":
                    mid = st.session_state.get("pdf_material_id")
                    chunks = st.session_state.get("pdf_chunks")
                    summary = st.session_state.get("pdf_summary")
                    if not chunks:
                        st.warning("Upload a PDF first")
                        st.stop()
                    quiz = smart_quiz_generator(
                        difficulty=difficulty, mcq_count=num_mcq, tf_count=num_tf,
                        material_id=mid, summary=summary, chunks=chunks,
                    )
                    save_quiz(user_id, mid, "pdf", difficulty, num_mcq, num_tf, quiz, settings.model_name)
                    st.session_state.pdf_quiz = quiz

                elif quiz_source == "🔗 From My URL Article":
                    mid = st.session_state.get("url_material_id")
                    chunks = st.session_state.get("url_chunks")
                    summary = st.session_state.get("url_summary")
                    if not chunks:
                        st.warning("Scrape a URL first")
                        st.stop()
                    quiz = smart_quiz_generator(
                        difficulty=difficulty, mcq_count=num_mcq, tf_count=num_tf,
                        material_id=mid, summary=summary, chunks=chunks,
                    )
                    save_quiz(user_id, mid, "url", difficulty, num_mcq, num_tf, quiz, settings.model_name)
                    st.session_state.url_quiz = quiz

                st.success("✅ Quiz generated!")
                st.rerun()

        except Exception as e:
            st.error(f"❌ {e}")

    if quiz_source == "🌍 From the Web" and "web_quiz" in st.session_state:
        display_quiz(st.session_state.web_quiz, "web")
    elif quiz_source == "📘 From My PDF File" and "pdf_quiz" in st.session_state:
        display_quiz(st.session_state.pdf_quiz, "pdf")
    elif quiz_source == "🔗 From My URL Article" and "url_quiz" in st.session_state:
        display_quiz(st.session_state.url_quiz, "url")
