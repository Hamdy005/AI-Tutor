import streamlit as st 

def display_quiz(quiz, source_prefix):

    st.header("📝 Take the Quiz")

    if not quiz:
        st.warning("No quiz found")
        return
    
    questions_cnt = 0

    with st.form(key=f"quiz_form_{source_prefix}"):

        # Multiple Choice Questions
        st.subheader("Multiple Choice Questions")
        mcqs = quiz.get("mcq", [])
        default_choice = "Choose the correct answer"

        for i, q in enumerate(mcqs):

            key = f"{source_prefix}_mcq_{i}"

            current_selection = st.session_state.user_answers.get(key, default_choice)
            options = [default_choice] + q.get("options", [])

            questions_cnt += 1
            default_index = options.index(current_selection) if current_selection in options else 0
            
            select = st.radio(

                f"{questions_cnt}- {q["question"]}",
                options=options,
                index=default_index,
                key=key,

            )
            st.session_state.user_answers[key] = select

        # True/False Questions
        st.subheader("True/False Questions")
        tfs = quiz.get("tf", [])

        for i, q in enumerate(tfs):

            key = f"{source_prefix}_tf_{i}"
            
            current_selection = st.session_state.user_answers.get(key, default_choice)
            options = [default_choice, 'True', 'False']
            
            default_index = options.index(current_selection) if current_selection in options else 0
            
            questions_cnt += 1
            select = st.radio(

                f"{questions_cnt}- {q["question"]}",
                options=options,
                index=default_index,
                key=key,

            )
            st.session_state.user_answers[key] = select

        # Submit Button inside the form
        submitted = st.form_submit_button("📤 Submit Quiz")
        
        if submitted:
            calculate_score(mcqs, tfs, source_prefix)

def calculate_score(mcqs, tfs, source_prefix):

    score = 0
    total = len(mcqs) + len(tfs)
    mcq_correct = 0
    tf_correct = 0

    st.write("---")
    st.subheader("📊 Quiz Results")
    
    # MCQ Correction
    st.write("**Multiple Choice Questions:**")
    for i, q in enumerate(mcqs):
        key = f"{source_prefix}_mcq_{i}"
        selected = st.session_state.user_answers.get(key)
        correct = q.get("answer")
        
        st.write(f"Q{i+1}: {q['question']}")
        st.write(f"  Your answer: {selected if selected else 'Not answered'}")
        st.write(f"  Correct answer: {correct}")
        
        if selected and correct and selected != "Choose the correct answer":
            selected_letter = selected.strip()[0].lower()
            correct_letter = correct.strip()[0].lower()  
            
            if selected_letter == correct_letter:
                score += 1
                mcq_correct += 1
                st.write("  ✅ Correct!")
            else:
                st.write("  ❌ Incorrect")
        else:
            st.write("  ⚠️ Not answered")
        st.write("---")

    # True/False Correction
    st.write("True/False Questions: ")
    for i, q in enumerate(tfs):
        key = f"{source_prefix}_tf_{i}"
        selected = st.session_state.user_answers.get(key)
        correct = q.get("answer")
        
        st.write(f"Q{len(mcqs)+i+1}: {q['question']}")
        st.write(f"  Your answer: {selected if selected else 'Not answered'}")
        st.write(f"  Correct answer: {correct}")
        
        if selected and selected != "Choose the correct answer" and correct is not None:
            selected_clean = str(selected).strip().lower()
            correct_clean = str(correct).strip().lower()
            
            if selected_clean == correct_clean:
                score += 1
                tf_correct += 1
                st.write("  ✅ Correct!")
            else:
                st.write("  ❌ Incorrect")
        else:
            st.write("  ⚠️ Not answered")
        st.write("---")

    # Display final results
    st.success(f"**Final Score: {score}/{total}**")
    st.info(f"Multiple Choice: {mcq_correct}/{len(mcqs)} correct")
    st.info(f"True or False: {tf_correct}/{len(tfs)} correct")