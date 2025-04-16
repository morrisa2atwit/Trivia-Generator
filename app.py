from flask import Flask, render_template, request
import openai
import json

app = Flask(__name__)


openai.api_key = "BLANK"
def generate_Questions(topic, num_Questions=10):
    prompt = (
        f"Generate {num_Questions} multiple-choice questions for the topic '{topic}'. "
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
    
    #Get the text from the response using attribute access
    result_Text = response.choices[0].message.content.strip()
    
    try:
        questions = json.loads(result_Text)
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
            #Generate 10 questions based on the topic.
            questions = generate_Questions(topic, num_Questions=10)
            if not questions:
                return "Not enough content to generate questions. Please try another topic.", 400
            return render_template('quiz.html', topic=topic, questions=questions)
        except Exception as e:
            return f"Error: {str(e)}", 400
    return render_template('index.html')

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz(): 
    results = []
    total_Questions = int(request.form.get("total_questions"))
    for i in range(1, total_Questions + 1):
        correct_Answer = request.form.get(f"correct_answer_{i}")
        user_Answer = request.form.get(f"user_answer_{i}", "").strip()
        is_Correct = (user_Answer.lower() == correct_Answer.lower()) if user_Answer else False
        results.append({
            'question_num': i,
            'correct_answer': correct_Answer,
            'user_answer': user_Answer,
            'is_correct': is_Correct
        })
    return render_template('results.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
