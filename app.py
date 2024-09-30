import openai
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os

# .env 파일에서 환경 변수를 불러오기
load_dotenv()

# Flask 애플리케이션 생성
app = Flask(__name__)

# OpenAI API 키 설정 (환경 변수에서 가져오기)
openai.api_key = os.getenv('FLASK_API_KEY')

# 이전 응답과 캐릭터 정보를 파일에서 읽어오는 함수
def read_previous_responses():
    responses = ''
    
    if os.path.exists('responses.txt'):
        with open('responses.txt', 'r', encoding='utf-8') as file:
            responses = file.read().strip()
    
    # if os.path.exists('characters.txt'):
    #     with open('characters.txt', 'r', encoding='utf-8') as file:
    #         characters = file.read().strip()

    return responses

@app.route('/')
def index():
    return render_template('zbgame/index.html')

# GPT-4 API 호출을 처리하는 엔드포인트
@app.route('/gpt', methods=['POST'])
def call_gpt():
    try:
        # 요청에서 사용자가 보낸 프롬프트 받기
        data = request.json
        prompt = data.get('prompt')

        if not prompt:
            return jsonify({"error": "프롬프트가 제공되지 않았습니다."}), 400
        
        # 이전 응답 및 캐릭터 정보 읽기
        previous_responses = read_previous_responses()

        # GPT-4 모델 호출
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": previous_responses},
                #{"role": "user", "content": characters},
                {"role": "user", "content": prompt}
            ],
            max_tokens=8000,
            temperature=0.5
        )

        # 응답에서 텍스트 추출
        generated_text = response.choices[0].message['content'].strip()

        # 응답 내용을 UTF-8 인코딩으로 파일에 저장
        with open('responses.txt', 'a', encoding='utf-8') as file:
            file.write(f"Prompt: {prompt}\nResponse: {generated_text}\n\n")

        return jsonify({"response": generated_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Flask 애플리케이션 실행
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
