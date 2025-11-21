// Basic lobby interactions - no complex logic
document.addEventListener("DOMContentLoaded", async () => {
  userinfo = localStorage.getItem('userinfo');
  userinfo = JSON.parse(userinfo);
  code = userinfo.room || userinfo.code;
  document.querySelector('.room-code').innerText = `Room: ${code}`;

  try{
    const response = await fetch(`http://127.0.0.1:8000/api/v1/player/?code=${encodeURIComponent(code)}`,
      {
        method: "GET",
        headers: {'Content-Type':'application/json'},
      });

      const res = await response.json();

      document.querySelector('.player-count').innerHTML = `Players: ${res.length}/8`;

      res.forEach(item => {
        document.getElementById('playersList').innerHTML += `
          <div class="player-item">
              <div class="player-info">
                  <span class="player-name">${item.username}</span>
              </div>
              <div class="player-status online">Online</div>
          </div>`;
        if (item.isAdmin) {
          document.querySelector('.player-info').innerHTML += `<span class="player-badge admin-badge">Admin</span>`
        }
      });
    }catch(error){
    alert("Can't connect to server");
    console.log("Error", error.message);
  }

  // Check if user is admin based on URL parameter
  const isAdmin = userinfo.isAdmin;

  // Show appropriate controls based on user role
  if (isAdmin) {
    document.getElementById("adminControls").style.display = "block"
    document.getElementById("playerWaiting").style.display = "none"

  //   document.getElementById('playersList').innerHTML = `
  //   <div class="player-item admin">
  //     <div class="player-info">
  //         <span class="player-name">${userinfo.username}</span>
  //         <span class="player-badge admin-badge">Admin</span>
  //     </div>
  //     <div class="player-status online">Online</div>
  //   </div>
  // `
  } else {
    document.getElementById("adminControls").style.display = "none"
    document.getElementById("playerWaiting").style.display = "block"
  }

  // document.getElementById('playersList').innerHTML += `
  //   <div class="player-item">
  //       <div class="player-info">
  //           <span class="player-name">${userinfo.username}</span>
  //       </div>
  //       <div class="player-status online">Online</div>
  //   </div>
  // // `
  
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
