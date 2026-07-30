document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.getElementById('toggleAiChatBtn');
  const closeBtn = document.getElementById('closeAiChatBtn');
  const chatWindow = document.getElementById('aiChatWindow');
  const chatForm = document.getElementById('aiChatForm');
  const chatInput = document.getElementById('aiChatInput');
  const messagesContainer = document.getElementById('aiChatMessages');

  // Toggle chat window visibility
  function toggleChat() {
    const isHidden = chatWindow.classList.contains('hidden');
    if (isHidden) {
      chatWindow.classList.remove('hidden');
      // trigger reflow
      void chatWindow.offsetWidth;
      chatWindow.classList.remove('scale-95', 'opacity-0');
      chatWindow.classList.add('scale-100', 'opacity-100');
      chatInput.focus();
    } else {
      chatWindow.classList.remove('scale-100', 'opacity-100');
      chatWindow.classList.add('scale-95', 'opacity-0');
      setTimeout(() => chatWindow.classList.add('hidden'), 300);
    }
  }

  toggleBtn?.addEventListener('click', toggleChat);
  closeBtn?.addEventListener('click', toggleChat);

  // Get CSRF token for Django POST request
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }

  // Append a message bubble
  function appendMessage(text, isUser = false) {
    const wrapper = document.createElement('div');
    wrapper.className = `flex ${isUser ? 'justify-end' : 'justify-start'}`;
    
    const bubble = document.createElement('div');
    bubble.className = `px-4 py-2.5 text-sm max-w-[85%] rounded-2xl ${
      isUser 
        ? 'bg-brand-600 text-white rounded-tr-sm shadow-md' 
        : 'bg-white border border-slate-100 shadow-sm text-slate-700 rounded-tl-sm'
    }`;
    
    // Convert newlines to breaks
    bubble.innerHTML = text.replace(/\n/g, '<br>');
    
    wrapper.appendChild(bubble);
    messagesContainer.appendChild(wrapper);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  // Handle form submission
  chatForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = chatInput.value.trim();
    if (!message) return;

    // Show user message
    appendMessage(message, true);
    chatInput.value = '';

    // Show loading indicator
    const loadingId = 'loading-' + Date.now();
    const loadingHtml = `
      <div id="${loadingId}" class="flex justify-start">
        <div class="bg-white border border-slate-100 shadow-sm text-slate-400 rounded-2xl rounded-tl-sm px-4 py-3 flex gap-1">
          <div class="w-1.5 h-1.5 bg-slate-300 rounded-full animate-bounce"></div>
          <div class="w-1.5 h-1.5 bg-slate-300 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
          <div class="w-1.5 h-1.5 bg-slate-300 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
        </div>
      </div>
    `;
    messagesContainer.insertAdjacentHTML('beforeend', loadingHtml);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    try {
      const response = await fetch('/api/ai-chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ message })
      });
      
      const data = await response.json();
      
      // Remove loading indicator
      document.getElementById(loadingId)?.remove();

      if (response.ok && data.response) {
        appendMessage(data.response, false);
      } else {
        appendMessage(data.error || 'Oops, something went wrong!', false);
      }
    } catch (error) {
      document.getElementById(loadingId)?.remove();
      appendMessage('Failed to connect to the server.', false);
    }
  });
});
