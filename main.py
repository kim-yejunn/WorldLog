import openai
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os
import sys
import json

# .env 파일에서 환경 변수를 불러오기
load_dotenv()

# Flask 애플리케이션 생성
app = Flask(__name__)

# OpenAI API 키 설정 (환경 변수에서 가져오기)
openai.api_key = os.getenv('OPENAI_API_KEY')

# 파일 경로 설정
history_path = 'history.txt'
rules_path = 'rules.json'

# JSON 파일 읽기
def load_rules_from_json():
    if os.path.exists(rules_path):
        with open(rules_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    logger.error("rules.json 파일을 찾을 수 없습니다.")
    return {}

# JSON 파일을 처음에 읽고 캐시에 저장
rules_cache = load_rules_from_json()

# history.txt 파일 초기화 함수
def initialize_history_file():
    if not os.path.exists(history_path) or os.stat(history_path).st_size == 0:
        with open(history_path, 'w', encoding='utf-8') as file:
            file.write("")

# history.txt 파일에서 이전 응답 불러오기
def read_previous_responses():
    responses = []
    initialize_history_file()

    if os.path.exists(history_path):
        with open(history_path, 'r', encoding='utf-8') as file:
            responses = file.readlines()

    return responses, rules_cache.get("intro", "")

# history.txt 파일에 데이터를 텍스트로 저장하는 함수
def write_to_responses(user_input, gpt_response):
    with open(history_path, 'a', encoding='utf-8') as file:
        file.write(f"User: {user_input}\n")
        file.write(f"Host: {gpt_response}\n")
        file.write("-" * 20 + "\n")  # 구분선 추가

@app.route('/')
def start():
    return render_template('start.html')

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/gpt', methods=['POST'])
def call_gpt():
    try:
        data = request.json
        prompt = data.get('prompt', "").strip()

        previous_responses, rules_content = read_previous_responses()

        if prompt.lower() == "trpg 마치기" and os.path.exists(history_path):
            os.remove(history_path)
            return jsonify({"response": "WorldLog TRPG를 마치겠습니다..! 재밌게 시간 보내주셔서 감사합니다!"})

        # GPT-4 모델 호출
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": json.dumps(rules_cache)},
                {"role": "user", "content": json.dumps(previous_responses)},
                {"role": "user", "content": prompt}
            ],
            max_tokens=8000,
            temperature=0.5
        )

        # 응답에서 텍스트 추출
        generated_text = response.choices[0].message.content.strip()

        # 응답 내용을 history.json에 저장
        write_to_responses(prompt, generated_text)

        return jsonify({"response": generated_text})

    except Exception as e:
        logger.error(f"오류 발생: {str(e)}")  # 오류 로그 기록
        return jsonify({"error": str(e)}), 500

@app.route('/end-trpg', methods=['POST'])
def end_trpg():
    if os.path.exists(history_path):
        os.remove(history_path)
        return jsonify({"response": "WorldLog TRPG를 마치겠습니다..! 재밌게 시간 보내주셔서 감사합니다!"})
    
    return jsonify({"response": "history.txt 파일이 존재하지 않습니다."})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
