from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
#from PyPDF2 import PdfReader
import json
import openai
import os
import fitz  # PyMuPDF
import random # 주사위를 굴리기 위한 랜덤 함수 추가.

app = Flask(__name__)
CORS(app)

# API Key 설정
openai.api_key = '키'

file_path = 'history.txt'

@app.route('/')
def home():
    return '홈 입니다.'

@app.route('/index')
def index():
    return render_template("index.html")

# properties.txt 파일의 내용을 읽는 함수
def read_properties_file():
    properties_file_path = os.path.join(os.getcwd(), 'properties.txt')
    if os.path.exists(properties_file_path):
        with open(properties_file_path, 'r', encoding='utf-8') as file:
            return file.read()
    else:
        return "게임 규칙을 찾을 수 없습니다."
    
# history.txt 파일을 생성
def write_to_history(user_input, gpt_response):
    with open('history.txt', 'a', encoding='utf-8') as history_file:
        history_file.write(f"사용자: {user_input}\n")
        history_file.write(f"진행자: {gpt_response}\n\n")
        
        
# data.json을 읽는 함수.
def load_game_state():
    try:
        with open('data.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        # 파일이 존재 하지 않는 경우 기본 값을 설정.
        return {
            "current_day": 1,
            "current_action": 0,
            "time_of_day": "아침",
            "max_actions_per_day": 5,
            "total_actions_today": 0
        }
        
# data.json 저장하는 함수.
def save_game_state(state):
    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump(state, file, ensure_ascii=False, indent=4)

# 랜덤 다이스 2개를 굴려줄 함수.
def roll_dice():
    return random.randint(1, 6) + random.randint(1, 6)

@app.route('/ask', methods=['POST'])
def ask_gpt():
    try:
        user_input = request.json.get('message')
        if not user_input:
            return jsonify({"error": "No input provided"}), 400
        
        # properties.txt 파일 내용 가져오기
        properties_content = read_properties_file()
        # Load the current game state
        game_state = load_game_state()
        
         # Handle player actions
        if "행동" in user_input:
            # Check if max actions for the day are reached
            if game_state["total_actions_today"] >= game_state["max_actions_per_day"]:
                return jsonify({"response": "오늘의 행동을 모두 소진했습니다. 숙면을 취하고 다음날로 넘어가세요."})

            # Roll dice for the action
            dice_result = roll_dice()
            game_state["total_actions_today"] += 1  # Increment the action count
            game_state["current_action"] += 1  # Track total actions
            game_state["time_of_day"] = update_time_of_day(game_state["total_actions_today"])  # Update the time of day

            # Save the updated game state to data.json
            save_game_state(game_state)

            # Construct the GPT response about the action
            response_text = f"주사위 결과는 {dice_result}입니다. 현재 {game_state['time_of_day']}이고, {game_state['total_actions_today']}번의 행동을 했습니다."
            return jsonify({"response": response_text})

        # Respond to questions like "몇일 차야?"
        if any(phrase in user_input for phrase in ["몇일 차", "몇일 차야", "지금 몇일 차야"]):
            return jsonify({"response": f"현재 {game_state['current_day']}일 차 진행 중입니다."})

        # Handle sleep and day reset
        if "숙면" in user_input:
            game_state["current_day"] += 1  # Move to the next day
            game_state["total_actions_today"] = 0  # Reset actions for the new day
            game_state["time_of_day"] = "아침"  # Start the new day at morning
            save_game_state(game_state)
            return jsonify({"response": f"하루가 지나갔습니다. 현재 {game_state['current_day']}일 차이며, 행동을 다시 시작할 수 있습니다."})
        
        # "TRPG 마치기" 입력 처리
        if user_input.strip().lower() == "trpg 마치기" and os.path.exists(file_path):
            os.remove(file_path)  # history.txt 파일 삭제
            return jsonify({"response": "ZombieWorld TRPG를 마치겠습니다..! 재밌게 시간 보내주셔서 감사합니다!"})


        # 새로운 GPT-4 API 호출 방식
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"다음은 TRPG 게임의 규칙입니다: {properties_content}"},
                {"role": "user", "content": user_input}
            ]
        )
        gpt_response = response['choices'][0]['message']['content']

        # gpt, 사용자의 내용을 history.txt에 작성
        write_to_history(user_input, gpt_response)
            
        return jsonify({"response": gpt_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
    

    
"""
# 답변을 했을때의 이 함수가 실행되는 것인데, 문제는 여러번 저 단어가 나올때마다 실행되다보니, 반복이 많아져 로드에도 부하가 생길 수 있고, 중복이 심해
# 그만큼 오류가 많이 발생 될 예정. 나중에 수정하기.

# Check if the GPT response includes certain trigger words (like '행동' or '숙면')
        if "행동" in gpt_response:
            # Handle player actions
            if game_state["total_actions_today"] >= game_state["max_actions_per_day"]:
                return jsonify({"response": "오늘의 행동을 모두 소진했습니다. 숙면을 취하고 다음날로 넘어가세요."})

            # Roll dice for the action
            dice_result = roll_dice()
            game_state["total_actions_today"] += 1  # Increment the action count
            game_state["current_action"] += 1  # Track total actions
            game_state["time_of_day"] = update_time_of_day(game_state["total_actions_today"])  # Update time of day

            # Save the updated game state to data.json
            save_game_state(game_state)

            # Append the result of the action to the GPT response
            gpt_response += f"\n주사위 결과는 {dice_result}입니다. 현재 {game_state['time_of_day']}이고, {game_state['total_actions_today']}번의 행동을 했습니다."

        elif "숙면" in gpt_response:
            # Handle sleep and day reset
            game_state["current_day"] += 1  # Move to the next day
            game_state["total_actions_today"] = 0  # Reset actions for the new day
            game_state["time_of_day"] = "아침"  # Start the new day in the morning

            # Save the updated game state to data.json
            save_game_state(game_state)

            # Append the day reset result to the GPT response
            gpt_response += f"\n하루가 지나갔습니다. 현재 {game_state['current_day']}일 차이며, 행동을 다시 시작할 수 있습니다."


"""
    
    
    
