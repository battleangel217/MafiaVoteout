document.addEventListener("DOMContentLoaded", () => {
  const chatBubble = document.getElementById("chatBubble")
  const chatModal = document.getElementById("chatModal")
  const closeChat = document.getElementById("closeChat")
  const chatSend = document.getElementById("chatSend")
  const chatInput = document.getElementById("chatInput")
  const chatMessages = document.getElementById("chatMessages")

  // Responses for common questions
  // const responses = {
  //   role: "There are 4 roles: Mafia (hidden killers), Detective (investigator), Doctor (protector), and Villager (innocent). Each has different abilities!",
  //   win: "Town wins if all mafia are eliminated. Mafia wins if they equal or outnumber the innocent players.",
  //   strategy:
  //     "Listen to discussions, observe voting patterns, and ask questions. Don't trust everyone! As mafia, create alibis.",
  //   mafia: "Mafia members vote during the day and eliminate innocents at night. They know each other's identities.",
  //   detective:
  //     "Detectives can investigate one player per night to learn their role. Share info strategically during the day.",
  //   doctor: "Doctors protect one player per night from being eliminated. You can protect yourself!",
  //   day: "During the day, all players discuss and vote to eliminate someone they think is mafia.",
  //   night: "At night, mafia kills, detective investigates, and doctor protects. Innocent players wait.",
  //   vote: "The player with the most votes during the day is eliminated and their role is revealed.",
  //   default:
  //     "I can help! Ask about roles, winning conditions, strategy, or specific phases like day/night. What would you like to know?",
  // }

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
      const response = await fetch('https://mafiavoteout-backend.onrender.com/api/v1/aiagent/',
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
