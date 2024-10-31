import openai
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os
import json
import logging

# .env 파일에서 환경 변수를 불러오기
load_dotenv()

# 로그 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask 애플리케이션 생성
app = Flask(__name__)

# OpenAI API 키 설정 (환경 변수에서 가져오기)
openai.api_key = os.getenv('OPENAI_API_KEY')

# 파일 경로 설정
history_path = 'history.json'
rules_path = 'rules.json'

# rules_path를 처음에 읽고 저장할 캐시
rules_cache = None  

# rules.json을 읽어오는 함수
def load_rules():
    global rules_cache
    if rules_cache is None and os.path.exists(rules_path):
        with open(rules_path, 'r', encoding='utf-8') as file:
            rules_cache = json.load(file)  # JSON 형식으로 읽기
            logger.info("rules.json 파일을 성공적으로 읽었습니다.")

# history.json의 데이터가 없을 경우 그 데이터를 한번 빈값으로 만들어주기
def initialize_history_file():
    if not os.path.exists(history_path) or os.stat(history_path).st_size == 0:
        with open(history_path, 'w', encoding='utf-8') as file:
            json.dump([], file)

# history.json과 rules.json 불러오기. 
def read_previous_responses():
    global rules_cache  # 전역 변수 선언
    responses = []
    
    initialize_history_file()  # 초기화 함수 호출

    if os.path.exists(history_path):
        with open(history_path, 'r', encoding='utf-8') as file:
            responses = json.load(file)

    # rules_cache가 딕셔너리인지 확인
    if not isinstance(rules_cache, dict):
        logger.error("rules_cache가 딕셔너리가 아닙니다.")
        rules_cache = {}  # 기본값 설정

    return responses, rules_cache

# history.json 파일을 업데이트하는 함수
def write_to_responses(user_input, gpt_response):
    data = []
    
    if os.path.exists(history_path):
        with open(history_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    
    # 데이터가 리스트인지 확인
    if isinstance(data, list):
        data.append({"user": user_input, "host": gpt_response})
    else:
        logger.error("history.json 파일의 데이터 형식이 리스트가 아닙니다.")  # 로그 기록
    
    with open(history_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# 애플리케이션 시작 시 rules.json 파일을 한 번 읽음
load_rules()

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
        data = request.json
        prompt = data.get('prompt', "").strip()

        previous_responses, _ = read_previous_responses()

        if prompt.lower() == "trpg 마치기" and os.path.exists(history_path):
            os.remove(history_path)
            return jsonify({"response": "WorldLog TRPG를 마치겠습니다..! 재밌게 시간 보내주셔서 감사합니다!"})

        # GPT-4 모델 호출
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
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
        os.remove(history_path)  # history.json 파일 삭제
        return jsonify({"response": "WorldLog TRPG를 마치겠습니다..! 재밌게 시간 보내주셔서 감사합니다!"})
    
    return jsonify({"response": "history.json 파일이 존재하지 않습니다."})

# Flask 애플리케이션 실행
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
