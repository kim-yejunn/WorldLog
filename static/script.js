document.getElementById('prompt').addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        document.getElementById('gpt-form').requestSubmit();
        document.getElementById('prompt').value = "";
    }
});

function focusTextarea() {
    document.getElementById('prompt').focus();
}

function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

// 버튼 클릭 이벤트 핸들러 함수
function handleButtonClick(value) {
    console.log(`버튼 클릭: ${value}`); // 디버깅용 로그
    document.getElementById('prompt').value = value; // 텍스트 영역에 값 설정
    document.getElementById('gpt-form').dispatchEvent(new Event('submit')); // 폼 제출 이벤트 발생
}

// 버튼 ID 배열과 이벤트 연결
['select1', 'select2', 'select3'].forEach((id, index) => {
    const button = document.getElementById(id);
    if (button) {
        button.addEventListener('click', () => handleButtonClick(index + 1));
        console.log(`${id} 버튼에 이벤트 리스너 추가됨`); // 디버깅용 로그
    } else {
        console.error(`${id} 버튼을 찾을 수 없습니다`); // 버튼이 없을 경우 로그
    }
});
document.getElementById('gpt-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const prompt = document.getElementById('prompt').value;

    try {
        const response = await fetch('/gpt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prompt }),
        });

        //asdad
        const data = await response.json(); 

        document.getElementById('response').textContent = data.response || data.error;

        // 응답 텍스트 표시
        document.getElementById('response').innerHTML = marked.parse(data.response);

        // 특정 단어 감지 및 이미지 추가
        handleResponseImages(data.response);

        // 응답 텍스트에서 불필요한 줄 바꿈을 하나의 줄로 줄임
        let cleanedResponse = data.response ? data.response.replace(/\n/g, '\n') : data.error;

        // Markdown을 HTML로 변환하여 표시
        document.getElementById('response').innerHTML = marked.parse(cleanedResponse);

    } catch (error) {
        document.getElementById('response').textContent = `Error: ${error.message}`;
    }

    prompt.value = '';
});

function handleResponseImages(responseText) {
    const imageContainer = document.getElementById('image-container');
    imageContainer.innerHTML = ''; // 기존 이미지를 지워줌

    // 단어와 이미지 매핑
    const wordImageMap = {
        //초기 시작
        'WorldLog TRPG 게임을 시작합니다!': 'select.png',
        'WorldLog TRPG 게임을 시작하겠습니다!': 'select.png',
        'WorldLog TRPG 게임에 오신 것을 환영합니다!': 'select.png',
        '사이버펑크': 'Cyberpunk.png',
        '좀비': 'Zombie.png',
        '포스트 아포칼립스 세계관을': 'apocalyptic.png',
        '우주 세계관을': 'universe.png',
        //판타지
        '판타지 왕국 세계를': 'Fantasy/fantasy.png',
        '판타지 세계를': 'Fantasy/fantasy.png',
        '용맹한 기사를 선택하셨군요': 'Fantasy/Knight.png',
        '전사를 선택': 'Fantasy/Knight.png',
        '마법사를 선택': 'Fantasy/wizard.png',
        '전사를 선택': 'Fantasy/Knight.png',
        
        //판타지 Day1
        '당신은 숲을 탐색하여 몬스터의 흔적을 찾기로 결정했습니다': 'Fantasy/Day1_Monster.png',
        '정보를 수집하기로 결정' : 'Fantasy/TalkToCitizen.png',
        '당신은 고대 유적지로' : 'Fantasy/ToRuins.png',
        '어두운 통로' : 'Fantasy/Tunnel.png',
        //디스토피아
        '디스토피아 미래 세계를': 'Dystopia/Dystopia.png'

    };

    let matchedKeyword = null; // 매칭된 키워드를 추적

    Object.keys(wordImageMap).some((keyword) => {
        if (responseText.includes(keyword)) {
            matchedKeyword = keyword;

            // 이미지 요소 생성
            const img = document.createElement('img');
            img.src = `/static/images/${wordImageMap[keyword]}`;
            img.alt = keyword;
            img.classList.add('response-image'); // CSS 스타일용 클래스
            imageContainer.appendChild(img);

            return true; 
        }
        return false; 
    });

    if (!matchedKeyword) {
        console.log('키워드가 없음: 기본 이미지를 표시합니다.');

        const defaultImg = document.createElement('img');
        defaultImg.src = `/static/images/default.png`; 
        defaultImg.alt = 'Default Image';
        defaultImg.classList.add('response-image');
        imageContainer.appendChild(defaultImg);
    }
}


// 새 "게임 재시작" 버튼 이벤트 핸들러
document.getElementById('restart').addEventListener('click', function() {
    document.getElementById('prompt').value = "게임 재시작"; // "게임 재시작"을 prompt에 입력
    document.getElementById('gpt-form').requestSubmit(); // 폼 제출
});

// 새 "게임 종료" 버튼 이벤트 핸들러
document.getElementById('gmend').addEventListener('click', function() {
    document.getElementById('prompt').value = "trpg 게임 종료"; // "trpg 게임 종료"을 prompt에 입력
    document.getElementById('gpt-form').requestSubmit(); // 폼 제출
});

// gmstart 버튼 클릭 시 textarea와 restart, gmend 버튼 표시
document.addEventListener("DOMContentLoaded", function() {
    const gmstart = document.getElementById("gmstart");
    const textarea = document.querySelector("textarea");
    const restart = document.getElementById("restart");
    const gmend = document.getElementById("gmend");
    const select1 = document.getElementById("select1");
    const select2 = document.getElementById("select2");
    const select3 = document.getElementById("select3");

    gmstart.addEventListener("click", function() {
        // textarea와 restart, gmend 버튼을 보이게 설정
        textarea.style.display = "block";
        restart.style.display = "block";
        gmend.style.display = "block";
        select1.style.display = "block";
        select2.style.display = "block";
        select3.style.display = "block";
        gmstart.style.display = "none"; // gmstart 버튼 숨기기 (선택 사항)

        // "trpg 게임 시작"을 입력하고 폼 제출
        document.getElementById('prompt').value = "trpg 게임 시작"; // "trpg 게임 시작"을 prompt에 입력
        document.getElementById('gpt-form').requestSubmit(); // 폼 제출
    });
});

function goToRoot() {
    window.location.href = window.location.origin; // 루트로 이동
}
