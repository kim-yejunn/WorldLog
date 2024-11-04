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

        const data = await response.json();
        document.getElementById('response').textContent = data.response || data.error;

        // 특정 조건에서 이미지를 추가하는 로직 예시
        if (prompt.includes("전사")) { // 예시로 "전사"라는 단어가 포함될 때
            const imgElement = document.createElement('img');
            imgElement.src = '/static/warrior.jpg'; // 이미지 경로 설정
            imgElement.alt = '전사 이미지';

            const container = document.getElementById('character-image-container');
            container.innerHTML = ''; // 기존 이미지가 있다면 제거
            container.appendChild(imgElement); // 새 이미지 추가
        }
    } catch (error) {
        document.getElementById('response').textContent = `Error: ${error.message}`;
    }
});

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

// 버튼1 클릭 이벤트 추가
document.getElementById('select1').addEventListener('click', () => {
    document.getElementById('prompt').value = '1'; // 텍스트 영역에 "1" 값 설정
    document.getElementById('gpt-form').dispatchEvent(new Event('submit')); // 폼 제출 이벤트 발생
});

// 버튼2 클릭 이벤트 추가
document.getElementById('select2').addEventListener('click', () => {
    document.getElementById('prompt').value = '2'; // 텍스트 영역에 "2" 값 설정
    document.getElementById('gpt-form').dispatchEvent(new Event('submit')); // 폼 제출 이벤트 발생
});

// 버튼3 클릭 이벤트 추가
document.getElementById('select3').addEventListener('click', () => {
    document.getElementById('prompt').value = '3'; // 텍스트 영역에 "3" 값 설정
    document.getElementById('gpt-form').dispatchEvent(new Event('submit')); // 폼 제출 이벤트 발생
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

        const data = await response.json();
        document.getElementById('response').textContent = data.response || data.error;
    } catch (error) {
        document.getElementById('response').textContent = `Error: ${error.message}`;
    }
});