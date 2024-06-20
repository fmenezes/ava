let conversationId = null;

function createMessage(role, message) {
    const chatBox = document.getElementById('chat-box');
    const userMessageElement = document.createElement('div');
    userMessageElement.className = 'message ' + role + '-message';
    userMessageElement.textContent = message;
    chatBox.appendChild(userMessageElement);
}

async function sendMessage() {
    const userInput = document.getElementById('user-input');
    const message = userInput.value.trim();
    if (message === '') return;
    userInput.value = '';

    if (!conversationId) {
        // Create a new conversation
        const response = await fetch('/conversations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        const data = await response.json();
        conversationId = data.id;
    }

    // Send message to the backend
    const response = await fetch(`/conversations/${conversationId}/messages`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: message }),
    });
    const data = await response.json();

    data.forEach(message => {
        createMessage(message.role, message.content)
    });

    // Scroll to the bottom of the chat box
    chatBox.scrollTop = chatBox.scrollHeight;
}
