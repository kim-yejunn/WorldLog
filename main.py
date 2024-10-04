import random
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

file_path = 'responses.txt'

# 이전 응답과 캐릭터 정보를 파일에서 읽어오는 함수
def read_previous_responses():
    responses = ''
    rules = ''
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            responses = file.read().strip()
    
    if os.path.exists('rules.txt'):
        with open('rules.txt', 'r', encoding='utf-8') as file:
            rules = file.read().strip()

    return responses, rules

# responses.txt 파일을 생성
def write_to_responses(user_input, gpt_response):
    with open('responses.txt', 'a', encoding='utf-8') as responses_file:
        responses_file.write(f"user: {user_input}\n")
        responses_file.write(f"host: {gpt_response}\n\n")

# 랜덤 다이스 2개를 굴려줄 함수.
def roll_dice():
    return random.randint(1, 6) + random.randint(1, 6)

@app.route('/')
def start():
    return render_template('start.html')

# /main 경로로 main.html 렌더링
@app.route('/main')
def main():
    return render_template('main.html')

# GPT-4 API 호출을 처리하는 엔드포인트
@app.route('/gpt', methods=['POST'])
def call_gpt():
    try:
        # 요청에서 사용자가 보낸 프롬프트 받기
        data = request.json
        prompt = data.get('prompt')

        if not prompt:
            return jsonify({"error": "프롬프트가 제공되지 않았습니다."}), 400
        
        # 이전 응답 및 규칙 정보 읽기
        previous_responses, rules = read_previous_responses()
        
        # "TRPG 마치기" 입력 처리
        if prompt.strip().lower() == "trpg 마치기" and os.path.exists(file_path):
            os.remove(file_path)  # response.txt 파일 삭제
            return jsonify({"response": "WorldLog TRPG를 마치겠습니다..! 재밌게 시간 보내주셔서 감사합니다!"})

        # GPT-4 모델 호출
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": rules},
                {"role": "user", "content": previous_responses},
                {"role": "user", "content": prompt}
            ],
            max_tokens=8000,
            temperature=0.5
        )

        # 응답에서 텍스트 추출
        generated_text = response.choices[0].message['content'].strip()

        # 응답 내용을 UTF-8 인코딩으로 파일에 저장
        write_to_responses(prompt, generated_text)
       
        return jsonify({"response": generated_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@app.route('/end-trpg', methods=['POST'])
def end_trpg():
    file_path = "responses.txt"

    if os.path.exists(file_path):
        os.remove(file_path)  # history.txt 파일 삭제
        return jsonify({"response": "WorldLog TRPG를 마치겠습니다..! 재밌게 시간 보내주셔서 감사합니다!"})
    
    return jsonify({"response": "responses.txt 파일이 존재하지 않습니다."})

# Flask 애플리케이션 실행
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
