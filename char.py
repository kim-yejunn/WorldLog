import openai
from flask import Flask, request, Response, jsonify, render_template
from dotenv import load_dotenv
import os

# .env 파일에서 환경 변수를 불러오기
load_dotenv()

# Flask 애플리케이션 생성
app = Flask(__name__)

# OpenAI API 키 설정 (환경 변수에서 가져오기)
openai.api_key = os.getenv('FLASK_API_KEY')

# 캐릭터 정보를 TXT 파일에 저장하는 함수
def save_character_to_file(character):
    try:
        with open('static/characters.txt', 'a', encoding='utf-8') as f:
            character_line = (
                f"id:{character['id']},name:{character['name']},class:{character['class']},"
                f"brain:{character['brain']},body:{character['body']},will:{character['will']},"
                f"guts:{character['guts']},fear:{character['fear']},infection:{character['infection']},"
                f"load:{character['load']},wound:{character['wound']}\n"
            )
            f.write(character_line)
    except Exception as e:
        print(f"파일 저장 중 오류 발생: {e}")

# 캐릭터 정보를 파일에서 불러오는 함수
def load_characters_from_file():
    characters = []
    try:
        with open('static/characters.txt', 'r', encoding='utf-8') as f:
            for line in f:
                character_data = dict(item.split(":") for item in line.strip().split(","))
                # 숫자형으로 변환
                character_data['id'] = int(character_data['id'])
                character_data['brain'] = int(character_data['brain'])
                character_data['body'] = int(character_data['body'])
                character_data['will'] = int(character_data['will'])
                character_data['guts'] = int(character_data['guts'])
                character_data['fear'] = int(character_data['fear'])
                character_data['infection'] = int(character_data['infection'])
                character_data['load'] = int(character_data['load'])
                character_data['wound'] = int(character_data['wound'])
                characters.append(character_data)
    except FileNotFoundError:
        print("characters.txt 파일을 찾을 수 없습니다. 새 파일을 생성합니다.")
    except Exception as e:
        print(f"파일 로드 중 오류 발생: {e}")
    return characters

# 이전 응답과 캐릭터 정보를 파일에서 읽어오는 함수
def read_previous_responses():
    responses = ''
    characters = ''
    
    if os.path.exists('responses.txt'):
        with open('responses.txt', 'r', encoding='utf-8') as file:
            responses = file.read().strip()
    
    if os.path.exists('characters.txt'):
        with open('characters.txt', 'r', encoding='utf-8') as file:
            characters = file.read().strip()

    return responses, characters

# 기본 경로는 game.py에서 처리하던 화면으로 렌더링
@app.route('/')
def game_page():
    return render_template('zbgame/game.html')

# /index 경로로 index.html 렌더링
@app.route('/index')
def index():
    return render_template('index.html')

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
        previous_responses, characters = read_previous_responses()

        # GPT-4 모델 호출
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": previous_responses},
                {"role": "user", "content": characters},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
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

# 캐릭터 생성 엔드포인트
@app.route('/api/characters', methods=['POST'])
def create_character():
    try:
        data = request.json
        characters = load_characters_from_file()
        character = {
            'id': len(characters) + 1,
            'name': data['name'],
            'class': data['class'],
            'brain': data['brain'],
            'body': data['body'],
            'will': data['will'],
            'guts': data['guts'],
            'fear': data['fear'],
            'infection': data['infection'],
            'load': data['load'],
            'wound': data['wound']
        }
        save_character_to_file(character)
        return Response(f"캐릭터가 생성되었습니다. ID: {character['id']}", status=201, mimetype='text/plain; charset=utf-8')
    except Exception as e:
        return Response(f"캐릭터 생성 중 오류 발생: {e}", status=500, mimetype='text/plain; charset=utf-8')

# 캐릭터 조회 엔드포인트
@app.route('/api/characters', methods=['GET'])
def get_characters():
    try:
        characters = load_characters_from_file()
        if not characters:
            return Response("캐릭터가 없습니다.", status=404, mimetype='text/plain; charset=utf-8')

        # 캐릭터 리스트를 텍스트로 응답
        response = "\n".join([
            f"ID: {c['id']}, 이름: {c['name']}, 직업: {c['class']}, 두뇌: {c['brain']}, 신체: {c['body']}, "
            f"투지: {c['will']}, 배짱: {c['guts']}, 공포: {c['fear']}, 감염: {c['infection']}, "
            f"하중: {c['load']}, 부상: {c['wound']}"
            for c in characters
        ])
        return Response(response, status=200, mimetype='text/plain; charset=utf-8')
    except Exception as e:
        return Response(f"캐릭터 목록을 불러오는 중 오류 발생: {e}", status=500, mimetype='text/plain; charset=utf-8')

# Flask 애플리케이션 실행
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8880)
