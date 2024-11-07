// document.getElementById('gpt-form').addEventListener('submit', async (event) => {
//     event.preventDefault();
//     const prompt = document.getElementById('prompt').value;

//     try {
//         const response = await fetch('/gpt', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//             },
//             body: JSON.stringify({ prompt }),
//         });

//         const data = await response.json();
//         document.getElementById('response').textContent = data.response || data.error;

//         // 특정 조건에서 이미지를 추가하는 로직 예시
//         if (prompt.includes("전사")) { // 예시로 "전사"라는 단어가 포함될 때
//             const imgElement = document.createElement('img');
//             imgElement.src = '/static/warrior.jpg'; // 이미지 경로 설정
//             imgElement.alt = '전사 이미지';

//             const container = document.getElementById('character-image-container');
//             container.innerHTML = ''; // 기존 이미지가 있다면 제거
//             container.appendChild(imgElement); // 새 이미지 추가
//         }
//     } catch (error) {
//         document.getElementById('response').textContent = `Error: ${error.message}`;
//     }
// });

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

        // 응답 텍스트에서 불필요한 줄 바꿈을 하나의 줄로 줄임
        let cleanedResponse = data.response ? data.response.replace(/\n/g, '\n') : data.error;

        // Markdown을 HTML로 변환하여 표시
        document.getElementById('response').innerHTML = marked.parse(cleanedResponse);

    } catch (error) {
        document.getElementById('response').textContent = `Error: ${error.message}`;
    }

    prompt.value = '';
});

// 새 "게임 재시작" 버튼 이벤트 핸들러
document.getElementById('restart').addEventListener('click', function() {
    document.getElementById('prompt').value = "게임 재시작"; // "게임 재시작"을 prompt에 입력
    document.getElementById('gpt-form').requestSubmit(); // 폼 제출
});
