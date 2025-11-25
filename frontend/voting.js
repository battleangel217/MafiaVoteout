// Basic UI interactions - no complex game logic
document.addEventListener("DOMContentLoaded", () => {
  let timeLeft = 20
  const timerElement = document.getElementById("timer")

  // Simple timer countdown for demo
  const timerInterval = setInterval(() => {
    timeLeft--
    timerElement.textContent = timeLeft

    // Add visual warnings
    if (timeLeft <= 5) {
      timerElement.className = "timer critical"
    } else if (timeLeft <= 10) {
      timerElement.className = "timer warning"
    }

    if (timeLeft <= 0) {
      clearInterval(timerInterval)
      // Show results sections
      document.getElementById("voteResults").style.display = "block"
      setTimeout(() => {
        document.getElementById("eliminationResult").style.display = "block"
      }, 2000)
    }
  }, 1000)

  // Vote button interactions
  document.querySelectorAll(".vote-btn").forEach((button) => {
    button.addEventListener("click", function () {
      if (!this.disabled) {
        // Reset all buttons
        document.querySelectorAll(".vote-btn").forEach((btn) => {
          btn.classList.remove("voted")
          btn.textContent = "Vote"
          btn.disabled = false
        })

        // Mark this button as voted
        this.classList.add("voted")
        this.textContent = "Voted"
        this.disabled = true

        // Add chat message
        const playerName = this.closest(".player-item").querySelector(".player-name").textContent
        addChatMessage("You", `voted for ${playerName.replace(" (You)", "")}`)
      }
    })
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

  // Next round button
  document.getElementById("nextRoundBtn").addEventListener("click", () => {
    window.location.href = "index.html"
  })
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
