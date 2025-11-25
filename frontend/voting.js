document.addEventListener("DOMContentLoaded", () => {
  userinfo = JSON.parse(localStorage.getItem('userinfo') || '{}');
  code = userinfo.room || userinfo.code;
  let timeLeft = 20
  const timerElement = document.getElementById("timer")

  const ws = new WebSocket(`ws://127.0.0.1:8000/ws/voting/${code}/`)

  ws.addEventListener('open', () => {
    ws.send(JSON.stringify({ action: 'join', username: userinfo.username}));
  });

  function renderPlayers(list) {
    const container = document.getElementById('playersList');
    container.innerHTML = '';

    // loop to render each player
    list.forEach(item => {
      if (userinfo.username === item.username){
        const mafiaBadge = item.isMafia ? `<span class="player-role">Mafia</span>` : '';
        container.innerHTML += `
          <div class="player-item" data-username="${item.username}">
            <div class="player-info">
              <span class="player-name">${item.username} (You)</span>
              ${mafiaBadge}
            </div>
            <button class="vote-btn">Vote</button>
          </div>`;
      }else{
        container.innerHTML += `
          <div class="player-item" data-username="${item.username}">
            <div class="player-info">
              <span class="player-name">${item.username}</span>
            </div>
            <button class="vote-btn">Vote</button>
          </div>`;
      }
    });

    return;
  }

  ws.addEventListener('message', (ev) => {
    const data = JSON.parse(ev.data);
    if (data.type === 'player_list') renderPlayers(data.players);
    if (data.type === 'player_left') {
      const el = document.querySelector(`#playersList .player-item[data-username="${data.player.username}"]`);
      if (el) el.removeChild()
      // const count = document.querySelectorAll('#playersList .player-item').length;
      // document.querySelector('.player-count').innerText = `Players: ${count-1}/8`;
      // nplayers --;
    }


    if (data.type === 'player_join') {
      let join_username = null;
      if (data.username === userinfo.username){
        join_username = "You";
      }else{
        join_username = data.username;
      }

      const chatMessages = document.getElementById("chatMessages");
      const messageElement = document.createElement("div");
      messageElement.className = "system-message";
      messageElement.innerText = `${join_username} joined the room`;
      chatMessages.appendChild(messageElement);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }


    if (data.type === 'chat_message'){
      let uname = null;
      if (data.username === userinfo.username){
        uname = "You";
      }else{
        uname = data.username;
      }
      addChatMessage(uname, data.message);
        
    }

    if (data.type === 'start_game'){
      window.location.href = "voting.html"
    }
  });

  ws.addEventListener('close', () => console.log('Socket closed'));
  ws.addEventListener('error', (e) => console.error('Socket error', e));

  // Simple timer countdown for demo
  // const timerInterval = setInterval(() => {
  //   timeLeft--
  //   timerElement.textContent = timeLeft

  //   // Add visual warnings
  //   if (timeLeft <= 5) {
  //     timerElement.className = "timer critical"
  //   } else if (timeLeft <= 10) {
  //     timerElement.className = "timer warning"
  //   }

  //   if (timeLeft <= 0) {
  //     clearInterval(timerInterval)
  //     // Show results sections
  //     document.getElementById("voteResults").style.display = "block"
  //     setTimeout(() => {
  //       document.getElementById("eliminationResult").style.display = "block"
  //     }, 2000)
  //   }
  // }, 1000)

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
      ws.send(JSON.stringify(
        {
          "action": "message",
          "username": userinfo.username,
          "message": message
        }
      ))
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
