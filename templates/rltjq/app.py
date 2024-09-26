from flask import Flask, render_template, request, jsonify
import openai
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# OpenAI API 키 설정 (환경 변수로부터 가져오기)
openai.api_key = os.getenv('OPENAI_API_KEY')

# 파일 경로 설정
chat_log_file = "chat_log.txt"

# 대화를 파일에 기록하는 함수
def save_to_file(user_message, gpt_response):
    with open(chat_log_file, 'a') as f:  # 'a'는 append 모드로 기존 파일에 내용을 추가
        f.write(f"User: {user_message}\n")
        f.write(f"GPT: {gpt_response}\n")
        f.write("\n")  # 빈 줄로 대화 구분

# index.html 렌더링
@app.route('/')
def index():
    return render_template('index.html')

# GPT와 상호작용하는 엔드포인트
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    
    if not user_input:
        return jsonify({'error': 'Message not provided'}), 400

    # GPT API 요청
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
                {
                    "role": "system",
                    "content": "You are the game master for a TRPG game. Your task is to guide the player through character creation, provide limited choices to progress the story, and manage randomness through dice rolls. You will communicate in Korean."
                },
                {
                    "role": "system",
                    "content": """
                    1. **게임 마스터 역할**: 당신은 TRPG 게임의 게임 마스터이며, 플레이어가 게임 세계에서 길을 잃지 않도록 이끌어야 합니다.

                    2. **캐릭터 생성**: 
                        - 플레이어에게 캐릭터 이름과 직업을 입력하게 하세요. 
                        - 이름과 직업은 10자 이하로 제한됩니다. 
                        - 모든 캐릭터 능력치는 주사위를 굴려서 랜덤으로 생성됩니다 (예: 1d6 또는 1d10).

                    3. **제한된 선택지 제공**: 
                        - 항상 플레이어에게 스토리 진행을 위한 3가지 선택지를 제시하세요.
                        - 플레이어가 선택지 이외의 답을 할 수 없도록 제한하세요.
                        - 불필요한 입력을 최소화하고 이야기의 흐름을 유지하세요.

                    4. **주사위 굴림**: 
                        - 주사위를 굴려서 플레이어의 행동 성공 여부를 결정하세요 (예: 1d20으로 스킬 체크, 1d6으로 데미지 계산).
                        - 주사위 결과에 따라 성공, 실패, 또는 부분 성공 여부를 명확히 나타내세요.

                    5. **게임 내 시간 제한**: 
                        - 게임은 정해진 일수의 인게임 시간으로 진행됩니다. 
                        - 게임 일수를 50일에서 100일 사이로 설정하세요.
                        - 플레이어가 설정된 일수에 도달하면 게임은 종료됩니다.

                    6. **TRPG에 집중**: 
                        - 플레이어가 TRPG 게임에만 집중하도록 유도하고, 다른 주제로 대화하지 않도록 하세요.
                        - 플레이어가 게임에서 벗어난 대화를 시도할 경우 다시 게임에 집중시키세요.
                    """
                }
        ],
        max_tokens=2000
    )
    
    gpt_response = response['choices'][0]['message']['content'].strip()

    # 대화를 파일에 저장
    save_to_file(user_input, gpt_response)

    # 응답 생성
    return jsonify({'response': gpt_response})

if not os.path.exists(chat_log_file):  # 로그 파일이 없으면 생성
    open(chat_log_file, 'w').close()

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # 5001 포트로 변경
