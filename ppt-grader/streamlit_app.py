import os
from flask import Flask, request, jsonify
from pptx import Presentation
import streamlit as st

app = Flask(__name__)

# Grading function with suggestions
def grade_ppt(file_path):
    try:
        prs = Presentation(file_path)
        scores = {}
        slides = [slide for slide in prs.slides]
        suggestions = []

        if len(slides) < 7:
            return {
                "error": "The PPT must have at least 7 slides for evaluation.",
                "suggestions": ["Add the missing slides to make a complete 7-slide presentation."]
            }

        def evaluate_text(text, keywords, full_score):
            matched_keywords = [keyword for keyword in keywords if keyword.lower() in text.lower()]
            return len(matched_keywords) / len(keywords) * full_score, matched_keywords

        def has_images(slide):
            return any(shape.shape_type == 13 for shape in slide.shapes)

        def check_across_slides(start_idx, keywords):
            for slide in slides[start_idx:]:
                slide_text = " ".join([shape.text for shape in slide.shapes if hasattr(shape, "text")])
                if any(keyword.lower() in slide_text.lower() for keyword in keywords):
                    return True
            return False

        # Slide 1: Name, Branch, Semester
        slide_1_text = " ".join([shape.text for shape in slides[0].shapes if hasattr(shape, "text")])
        score, matched = evaluate_text(slide_1_text, ["name", "branch", "semester"], 5)
        scores["Slide 1"] = score
        if score < 5:
            suggestions.append("Slide 1 is missing key details like Name, Branch, or Semester.")
        if has_images(slides[0]):
            scores["Slide 1"] += 1

        # Slide 2: 3 ideas with summaries
        slide_2_text = " ".join([shape.text for shape in slides[1].shapes if hasattr(shape, "text")])
        idea_lines = slide_2_text.splitlines()
        scores["Slide 2"] = min(len(idea_lines), 3) / 3 * 5
        if scores["Slide 2"] < 5:
            suggestions.append("Slide 2 should have 3 distinct ideas, each with a crisp 1-liner summary.")
        if has_images(slides[1]):
            scores["Slide 2"] += 1

        # Slides 3, 4, 5: Problem, Solution, Market, etc.
        for i in range(3):
            slide_text = " ".join([shape.text for shape in slides[2 + i].shapes if hasattr(shape, "text")])
            keywords = ["problem", "solution", "market", "growth", "competition"]
            score, matched = evaluate_text(slide_text, keywords, 20)
            scores[f"Slide {i + 3}"] = score
            if score < 20:
                missing = [k for k in keywords if k not in matched]
                suggestions.append(f"Slide {i + 3} is missing details about: {', '.join(missing)}.")
            if has_images(slides[2 + i]):
                scores[f"Slide {i + 3}"] += 1

        # Slide 6: Metrics and validation
        slide_6_text = " ".join([shape.text for shape in slides[5].shapes if hasattr(shape, "text")])
        metrics_keywords = ["ctr", "cpc", "cpa"]
        market_keywords = ["market size", "market growth", "competition"]
        metrics_score, _ = evaluate_text(slide_6_text, metrics_keywords, 10)
        market_score, _ = evaluate_text(slide_6_text, market_keywords, 10)
        scores["Slide 6"] = metrics_score + market_score
        if metrics_score < 10 or market_score < 10:
            suggestions.append("Slide 6 should include CTR, CPC, CPA metrics, and clarity about market size, growth, and competition.")
        if has_images(slides[5]):
            scores["Slide 6"] += 1

        # Slide 7: Justification
        slide_7_text = " ".join([shape.text for shape in slides[6].shapes if hasattr(shape, "text")])
        uniqueness_keywords = ["unique", "skills", "quality"]
        score, matched = evaluate_text(slide_7_text, uniqueness_keywords, 10)
        if score == 0 and not check_across_slides(7, uniqueness_keywords):
            scores["Slide 7"] = 0
            suggestions.append("Slide 7 should justify why this idea is unique and why you have the skills to execute it successfully.")
        else:
            scores["Slide 7"] = score
        if has_images(slides[6]):
            scores["Slide 7"] += 1

        total_score = sum(scores.values())
        return {"scores": scores, "total_score": total_score, "suggestions": suggestions}
    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def index():
    return "Welcome to the Enhanced PPT Grader API."

@app.route('/grade', methods=['POST'])
def grade():
    if 'ppt' not in request.files:
        return jsonify({"error": "No file uploaded."}), 400

    ppt_file = request.files['ppt']
    file_path = os.path.join("uploads", ppt_file.filename)
    ppt_file.save(file_path)

    result = grade_ppt(file_path)
    os.remove(file_path)
    return jsonify(result)

# Streamlit Front-end
st.title("Interactive PPT Grader for I&ET Assignment")
st.markdown("Upload your PPT to get a detailed evaluation along with actionable feedback for improvement.")

uploaded_file = st.file_uploader("Upload your PPT file", type=["pptx"])

if uploaded_file is not None:
    # Save file temporarily
    file_path = os.path.join("uploads", uploaded_file.name)
    os.makedirs("uploads", exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Grade the PPT
    result = grade_ppt(file_path)
    os.remove(file_path)

    # Display results
    if "error" in result:
        st.error(result["error"])
    else:
        st.subheader("Grading Report")
        total_score = result["total_score"]
        for criteria, score in result["scores"].items():
            st.write(f"**{criteria}:** {score:.2f}")
        st.write(f"**Total Score:** {total_score:.2f}%")

        st.subheader("Suggestions for Improvement")
        if result["suggestions"]:
            for suggestion in result["suggestions"]:
                st.write(f"- {suggestion}")
        else:
            st.write("Great job! Your presentation meets all the criteria.")
