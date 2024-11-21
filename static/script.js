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
        '판타지': 'fantasy.png',
        '사이버펑크': 'Cyberpunk.png',
        '좀비': 'Zombie.png',
        '아포칼립스': 'apocalyptic.png',
        '우주': 'universe.png',
    };

    // 응답 텍스트에서 단어가 포함된 경우 이미지를 추가
    Object.keys(wordImageMap).forEach((keyword) => {
        if (responseText.includes(keyword)) {
            const img = document.createElement('img');
            img.src = `/static/images/${wordImageMap[keyword]}`;
            img.alt = keyword;
            img.classList.add('response-image'); // 스타일을 위한 클래스
            imageContainer.appendChild(img);
        }
    });
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
