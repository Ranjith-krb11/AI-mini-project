from core.llm_setup import get_llm

def generate_study_plan(subject, exam_date, hours_per_day, topics):
    llm = get_llm()

    prompt = f"""
    Create a smart study plan.

    Subject: {subject}
    Exam Date: {exam_date}
    Hours per day: {hours_per_day}
    Topics: {topics}

    Give day-wise study schedule with revision and quiz time.
    """

    response = llm.generate_content(prompt)
    return response.text