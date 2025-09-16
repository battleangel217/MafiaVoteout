// Basic lobby interactions - no complex logic
document.addEventListener("DOMContentLoaded", () => {
  // Check if user is admin based on URL parameter
  const urlParams = new URLSearchParams(window.location.search)
  const isAdmin = urlParams.get("admin") === "true"

  // Show appropriate controls based on user role
  if (isAdmin) {
    document.getElementById("adminControls").style.display = "block"
    document.getElementById("playerWaiting").style.display = "none"
  } else {
    document.getElementById("adminControls").style.display = "none"
    document.getElementById("playerWaiting").style.display = "block"
  }

  // Start game button (admin only)
  document.getElementById("startGameBtn").addEventListener("click", () => {
    window.location.href = "voting.html"
  })

  // Chat functionality
  const chatInput = document.getElementById("chatInput")
  const sendBtn = document.getElementById("sendBtn")

  function sendMessage() {
    const message = chatInput.value.trim()
    if (message) {
      addChatMessage("You", message)
      chatInput.value = ""
    }
  }

  sendBtn.addEventListener("click", sendMessage)
  chatInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      sendMessage()
    }
  })

  // Helper function to add chat messages
  function addChatMessage(username, message) {
    const chatMessages = document.getElementById("chatMessages")
    const messageElement = document.createElement("div")
    messageElement.className = "chat-message"
    messageElement.innerHTML = `<span class="username">${username}:</span> ${message}`
    chatMessages.appendChild(messageElement)
    chatMessages.scrollTop = chatMessages.scrollHeight
  }
})
