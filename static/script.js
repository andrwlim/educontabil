document.addEventListener('DOMContentLoaded', function() {
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const chatBox = document.getElementById('chat-box');

    const questions = [
        { text: "Qual o tamanho da sua empresa?", options: ["Grande Porte", "Médio Porte", "Pequeno Porte"] },
        { text: "Você é MEI (Microempreendedor Individual)?", options: ["Sim", "Não"] },
        { text: "Há quanto tempo sua empresa está ativa?", options: ["Há menos de 1 ano", "Há mais de 1 ano", "Há mais de 5 anos", "Há mais de 10 anos"] },
        { text: "Última pergunta: sobre o que é o seu negócio? Responda com suas palavras. Ex.: pesca, mercearia, manicure.", options: [] }
    ];
    let currentQuestionIndex = 0;
    let responses = [];

    function displayQuestion() {
        if (currentQuestionIndex < questions.length) {
            const question = questions[currentQuestionIndex];
            const questionElement = document.createElement('div');
            questionElement.className = 'question';
            questionElement.textContent = question.text;

            chatBox.appendChild(questionElement);
            chatBox.scrollTop = chatBox.scrollHeight;

            if (question.options.length > 0) {
                const optionsContainer = document.createElement('div');
                optionsContainer.className = 'options-container';

                question.options.forEach(option => {
                    const button = document.createElement('button');
                    button.textContent = option;
                    button.className = 'option-button btn btn-outline-success m-2';
                    button.addEventListener('click', () => handleOptionSelect(option, button));
                    optionsContainer.appendChild(button);
                });

                chatBox.appendChild(optionsContainer);
                chatBox.scrollTop = chatBox.scrollHeight;
            } else {
                chatInput.style.display = 'block';
                sendButton.style.display = 'block';
            }
        } else {
            // All questions answered
            addMessageToChatBox('Ótimo. Agora conheço melhor sua empresa. O que você gostaria de saber?', 'bot-message');
            chatInput.style.display = 'block';
            sendButton.style.display = 'block';
        }
    }

    function handleOptionSelect(option, button) {
        responses.push(option);
        currentQuestionIndex++;
        displayQuestion();
        // Adicionar classe ao botão clicado e alterar cor e texto
        button.style.backgroundColor = '#28a745';
        button.style.color = '#fff';
    }

    function addMessageToChatBox(message, messageType) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${messageType}`;
        messageElement.innerHTML = message;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    sendButton.addEventListener('click', function() {
        const message = chatInput.value.trim();
        if (message !== '') {
            if (currentQuestionIndex >= questions.length) {
                addMessageToChatBox(message, 'user-message');
                sendMessageToServer(message);
            } else {
                responses.push(message);
                currentQuestionIndex++;
                displayQuestion();
            }
            chatInput.value = '';
            // Adicionar classe ao botão clicado e alterar cor e texto
            sendButton.style.backgroundColor = '#28a745';
            sendButton.style.color = '#fff';
        }
    });

    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendButton.click();
        }
    });

    function sendMessageToServer(message) {
        fetch('/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            addMessageToChatBox(data.message, 'bot-message');
        })
        .catch(error => console.error('Error:', error));
    }

    // Start the question flow
    displayQuestion();
});
