from flask import Flask, render_template, request
import openai
import json

app = Flask(__name__)

# Set your OpenAI API key (replace with your actual API key)
openai.api_key = "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"

def generate_questions_with_openai(topic, num_questions=10):
    prompt = (
        f"Generate {num_questions} multiple-choice, Jeopardy-style quiz questions for the topic '{topic}'. "
        "Each question should include a clear and concise clue, four options (one correct answer and three distractors), "
        "and specify the correct answer. Do not include any questions that are not relevant to the topic. "
        "Output the questions in JSON format as a list of objects, each with keys: 'question', 'options', and 'answer'."
    )
    
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert quiz master who creates challenging, topic-focused Jeopardy-style multiple-choice questions."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=2000
    )
    
    # Get the text from the response using attribute access.
    result_text = response.choices[0].message.content.strip()
    
    try:
        questions = json.loads(result_text)
        if not all('question' in q and 'options' in q and 'answer' in q for q in questions):
            raise ValueError("JSON structure does not match expected format")
    except Exception as e:
        print("Error parsing API response:", e)
        questions = []
    return questions

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        topic = request.form.get('topic')
        try:
            # Generate 10 questions using the OpenAI API based on the topic.
            questions = generate_questions_with_openai(topic, num_questions=10)
            if not questions:
                return "Not enough content to generate questions. Please try another topic.", 400
            return render_template('quiz.html', topic=topic, questions=questions)
        except Exception as e:
            return f"Error: {str(e)}", 400
    return render_template('index.html')

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    results = []
    total_questions = int(request.form.get("total_questions"))
    for i in range(1, total_questions + 1):
        correct_answer = request.form.get(f"correct_answer_{i}")
        user_answer = request.form.get(f"user_answer_{i}", "").strip()
        is_correct = (user_answer.lower() == correct_answer.lower()) if user_answer else False
        results.append({
            'question_num': i,
            'correct_answer': correct_answer,
            'user_answer': user_answer,
            'is_correct': is_correct
        })
    return render_template('results.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
