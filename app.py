from flask import Flask, request, render_template, redirect, url_for
import joblib
import pandas as pd

# Flask 앱 초기화
app = Flask(__name__)

# 저장된 KNN 모델 불러오기
model = joblib.load("C:/project/stopbang_task/knn_stopbang_model5.pkl")

# STOP-BANG 점수에 따른 위험도와 확률을 매핑
def get_risk_level_and_probability(total_score):
    if total_score <= 2:
        return '안전 (Low Risk)', '5%'
    elif 3 <= total_score <= 4:
        return '경증 (Mild Risk)', '20%'
    elif 5 <= total_score <= 6:
        return '중등증 (Moderate Risk)', '40%'
    else:
        return '중증 (Severe Risk)', '80%'

# 홈 페이지
@app.route('/')
def consent():
    return render_template('consent.html')

# 개인정보 동의 처리
@app.route('/consent', methods=['POST'])
def consent_post():
    if request.form.get('consent') == 'on':
        return redirect(url_for('user_type'))
    else:
        return "개인정보 동의가 필요합니다.", 400

# 회원/비회원 선택 페이지
@app.route('/user_type')
def user_type():
    return render_template('user_type.html')

# 회원/비회원 버튼 처리
@app.route('/user_selection', methods=['POST'])
def user_selection():
    user_type = request.form.get('user_type')
    if user_type == 'non_member':
        return redirect(url_for('home'))
    elif user_type == 'member':
        return redirect(url_for('login'))
    return "잘못된 요청입니다.", 400

# 로그인 페이지
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 로그인 처리 로직 추가 가능
        return redirect(url_for('home'))
    return render_template('login.html')

# STOP-BANG 설문지 페이지
@app.route('/home')
def home():
    return render_template('index.html')

# 예측 수행
# 예측 수행
@app.route('/result', methods=['POST'])
def predict():
    try:
        # 요청된 폼 데이터를 출력하여 확인
        print(request.form)

        # STOP 항목
        snore = int(request.form['Snore'])
        tired = int(request.form['Tired'])
        apnea = int(request.form['Apnea'])
        htn = int(request.form['HTN'])

        # BANG 항목
        bmi = int(request.form['BMI'])
        age = int(request.form['Age'])
        neck = int(request.form['NeckCircumference'])
        sex = int(request.form['Sex'])

        # 각 항목의 합산 점수 계산
        stop_score = snore + tired + apnea + htn
        bang_score = bmi + age + neck + sex
        total_score = stop_score + bang_score

        # 위험도 및 확률 계산
        risk_level, risk_probability = get_risk_level_and_probability(total_score)

        # 모델 예측 확률 계산 (수면무호흡 확률)
        # DataFrame 형태로 변환
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
        # 피처의 순서 및 이름을 일치시키기 위해 사용된 피처를 명시적으로 설정합니다.
        input_data = input_data[['Snore loudly', 'Tired', 'Observe', 'Pressure', 'BMI', 'Age', 'Neck circumference', 'Sex', 'STOP', 'BANG', 'Total']]

        prediction_proba = model.predict_proba(input_data)[0][1]  # 예측 확률 (1인 클래스의 확률)

        # 결과 반환
        result = {
            'stop_score': stop_score,
            'bang_score': bang_score,
            'total_score': total_score,
            'risk_level': risk_level,
            'risk_probability': risk_probability,
            'prediction_proba': round(prediction_proba * 100, 2)  # 수면무호흡 확률
        }

        # 디버깅: result 딕셔너리를 출력하여 확인
        print("Result Dictionary:", result)
        return render_template('result.html', result=result)
    
    except Exception as e:
        # 다른 예외가 발생한 경우
        print(f"Error: {e}")
        return "Error occurred while processing the form data", 400


if __name__ == '__main__':
    app.run(debug=True)