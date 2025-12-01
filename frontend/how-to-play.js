document.addEventListener("DOMContentLoaded", () => {
  const chatBubble = document.getElementById("chatBubble")
  const chatModal = document.getElementById("chatModal")
  const closeChat = document.getElementById("closeChat")
  const chatSend = document.getElementById("chatSend")
  const chatInput = document.getElementById("chatInput")
  const chatMessages = document.getElementById("chatMessages")

  // Responses for common questions
  const responses = {
    role: "There are 4 roles: Mafia (hidden killers), Detective (investigator), Doctor (protector), and Villager (innocent). Each has different abilities!",
    win: "Town wins if all mafia are eliminated. Mafia wins if they equal or outnumber the innocent players.",
    strategy:
      "Listen to discussions, observe voting patterns, and ask questions. Don't trust everyone! As mafia, create alibis.",
    mafia: "Mafia members vote during the day and eliminate innocents at night. They know each other's identities.",
    detective:
      "Detectives can investigate one player per night to learn their role. Share info strategically during the day.",
    doctor: "Doctors protect one player per night from being eliminated. You can protect yourself!",
    day: "During the day, all players discuss and vote to eliminate someone they think is mafia.",
    night: "At night, mafia kills, detective investigates, and doctor protects. Innocent players wait.",
    vote: "The player with the most votes during the day is eliminated and their role is revealed.",
    default:
      "I can help! Ask about roles, winning conditions, strategy, or specific phases like day/night. What would you like to know?",
  }

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
  function sendMessage() {
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
    let response = responses.default
    const lowerMessage = message.toLowerCase()

    for (const key in responses) {
      if (lowerMessage.includes(key)) {
        response = responses[key]
        break
      }
    }

    // Add bot response after a delay
    setTimeout(() => {
      typingBubble.remove()

      const botMessage = document.createElement("div")
      botMessage.className = "chat-message bot-message"
      botMessage.innerHTML = `<p>${response}</p>`
      chatMessages.appendChild(botMessage)
      chatMessages.scrollTop = chatMessages.scrollHeight
    }, 300)

    chatMessages.scrollTop = chatMessages.scrollHeight
  }

  chatSend.addEventListener("click", sendMessage)
  chatInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      sendMessage()
    }
  })
})
