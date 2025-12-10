document.addEventListener("DOMContentLoaded", () => {
  const chatBubble = document.getElementById("chatBubble")
  const chatModal = document.getElementById("chatModal")
  const closeChat = document.getElementById("closeChat")
  const chatSend = document.getElementById("chatSend")
  const chatInput = document.getElementById("chatInput")
  const chatMessages = document.getElementById("chatMessages")

  // Toggle chat modal
  chatBubble.addEventListener("click", () => {
    chatModal.classList.toggle("active")
    chatBubble.classList.toggle("active")
    if (chatModal.classList.contains("active")) {
      chatInput.focus()
    }
  })

  closeChat.addEventListener("click", () => {
    chatModal.classList.remove("active")
    chatBubble.classList.remove("active")
  })

  document.addEventListener("click", (event) => {
    if (!chatModal.contains(event.target) && !chatBubble.contains(event.target)) {
      if (chatModal.classList.contains("active")) {
        chatModal.classList.remove("active")
        chatBubble.classList.remove("active")
      }
    }
  })

  // Close chat with Escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" || e.key === "Esc") {
      if (chatModal.classList.contains("active")) {
        chatModal.classList.remove("active")
        chatBubble.classList.remove("active")
        // optionally remove focus from input
        if (document.activeElement === chatInput) chatInput.blur()
      }
    }
  })

  // Send message
  async function sendMessage() {
    const message = chatInput.value.trim()
    if (!message) return

    // Add user message
    const userMessage = document.createElement("div")
    userMessage.className = "chat-message user-message"
    userMessage.innerHTML = `<p>${message}</p>`
    chatMessages.appendChild(userMessage)

    chatInput.value = ""

    const typingBubble = document.createElement("div")
    typingBubble.className = "chat-message bot-message typing-indicator"
    typingBubble.innerHTML = `<div class="typing-dots"><span></span><span></span><span></span></div>`
    chatMessages.appendChild(typingBubble)
    chatMessages.scrollTop = chatMessages.scrollHeight

    // Get response
    // let response = responses.default
    // for (const key in responses) {
    //   if (lowerMessage.includes(key)) {
    //     response = responses[key]
    //     break
    //   }
    // }

    const data = {
      "message": message
    }

    try{
      const response = await fetch('https://mafiavoteout-backend1.onrender.com/api/v1/aiagent/',
        {
          method: "POST",
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(data)
        });

        const res = await response.json();
        const aiResponse = marked.parse(res.message);
        console.log(aiResponse);
        typingBubble.remove()

        const botMessage = document.createElement("div")
        botMessage.className = "chat-message bot-message"
        botMessage.innerHTML = aiResponse
        chatMessages.appendChild(botMessage)
        chatMessages.scrollTop = chatMessages.scrollHeight

        chatMessages.scrollTop = chatMessages.scrollHeight
    }catch(error){
      typingBubble.remove()

      const botMessage = document.createElement("div")
      botMessage.className = "chat-message bot-message"
      botMessage.innerHTML = `<p>Can't connect to server</p>`
      chatMessages.appendChild(botMessage)
      chatMessages.scrollTop = chatMessages.scrollHeight

      chatMessages.scrollTop = chatMessages.scrollHeight
      console.log("Error", error.message)
    }


    // Add bot response after a delay
   
  }

  chatSend.addEventListener("click", sendMessage)
  chatInput.addEventListener("keypress", async (e) => {
    if (e.key === "Enter") {
      sendMessage()
    }
  })
})
