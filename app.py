from flask import Flask, request, render_template, redirect, url_for
import joblib
import pandas as pd
import os

app = Flask(__name__)

# 현재 app.py가 위치한 디렉토리 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 상대경로로 모델 로드
model_path = os.path.join(BASE_DIR, "knn_stopbang_model5.pkl")
model = joblib.load(model_path)

def get_risk_level_and_probability(total_score):
    if total_score <= 2:
        return '안전 (Low Risk)', '5%'
    elif 3 <= total_score <= 4:
        return '경증 (Mild Risk)', '20%'
    elif 5 <= total_score <= 6:
        return '중등증 (Moderate Risk)', '40%'
    else:
        return '중증 (Severe Risk)', '80%'

@app.route('/')
def consent():
    return render_template('consent.html')

@app.route('/consent', methods=['POST'])
def consent_post():
    if request.form.get('consent') == 'on':
        return redirect(url_for('user_type'))
    else:
        return "개인정보 동의가 필요합니다.", 400

@app.route('/user_type')
def user_type():
    return render_template('user_type.html')

@app.route('/user_selection', methods=['POST'])
def user_selection():
    user_type = request.form.get('user_type')
    if user_type == 'non_member':
        return redirect(url_for('home'))
    elif user_type == 'member':
        return redirect(url_for('login'))
    return "잘못된 요청입니다.", 400

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 로그인 처리 로직 추가 가능
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        print(request.form)

        snore = int(request.form['Snore'])
        tired = int(request.form['Tired'])
        apnea = int(request.form['Apnea'])
        htn = int(request.form['HTN'])

        bmi = int(request.form['BMI'])
        age = int(request.form['Age'])
        neck = int(request.form['NeckCircumference'])
        sex = int(request.form['Sex'])

        stop_score = snore + tired + apnea + htn
        bang_score = bmi + age + neck + sex
        total_score = stop_score + bang_score

        risk_level, risk_probability = get_risk_level_and_probability(total_score)

        input_data = pd.DataFrame([{
            'Snore loudly': snore,
            'Tired': tired,
            'Observe': apnea,
            'Pressure': htn,
            'BMI': bmi,
            'Age': age,
            'Neck circumference': neck,
            'Sex': sex,
            'STOP': stop_score,
            'BANG': bang_score,
            'Total': total_score
        }])

        input_data = input_data[['Snore loudly', 'Tired', 'Observe', 'Pressure', 'BMI', 'Age', 'Neck circumference', 'Sex', 'STOP', 'BANG', 'Total']]

        prediction_proba = model.predict_proba(input_data)[0][1]

        result = {
            'stop_score': stop_score,
            'bang_score': bang_score,
            'total_score': total_score,
            'risk_level': risk_level,
            'risk_probability': risk_probability,
            'prediction_proba': round(prediction_proba * 100, 2)
        }

        print("Result Dictionary:", result)
        return render_template('result.html', result=result)

    except Exception as e:
        print(f"Error: {e}")
        return "Error occurred while processing the form data", 400

if __name__ == '__main__':
    app.run(debug=True)
