document.addEventListener("DOMContentLoaded", async () => {
  userinfo = JSON.parse(localStorage.getItem('userinfo') || '{}');
  code = userinfo.room || userinfo.code;
  document.querySelector('.room-code').innerText = `Room: ${code}`;

  const wsProto = location.protocol === 'https:' ? 'wss' : 'ws';
  // const ws = new WebSocket(`wss://mafiavoteout-backend.onrender.com/ws/lobby/${code}/`);
  const ws = new WebSocket(`ws://127.0.0.1:8000/ws/lobby/${code}/`);

  // Sends join message
  ws.addEventListener('open', () => {
    ws.send(JSON.stringify({ action: 'join', username: userinfo.username}));
  });

  //render players from db
  function renderPlayers(list) {
    const container = document.getElementById('playersList');
    // build HTML for players first
    document.querySelector('.player-count').innerText = `Players: ${list.length}/15`;
    self.nplayers = list.length;
    let html = '';
    list.forEach(item => {
      let status = item.online ? 'Online' : 'Offline';
      if (userinfo.username === item.username){
        const adminBadge = item.isAdmin ? `<span class="player-badge admin-badge">Admin</span>` : '';
        html += `
          <div class="player-item" data-username="${item.username}">
            <div class="player-info">
              <span class="player-name">${item.username} (You)</span>
              ${adminBadge}
            </div>
            <div class="player-status ${status.toLocaleLowerCase()}">${status}</div>
          </div>`;
      } else {
        const adminBadge = item.isAdmin ? `<span class="player-badge admin-badge">Admin</span>` : '';
        html += `
          <div class="player-item" data-username="${item.username}">
            <div class="player-info">
              <span class="player-name">${item.username}</span>
              ${adminBadge}
            </div>
            <div class="player-status ${status.toLocaleLowerCase()}">${status}</div>
          </div>`;
      }
    });

    // gracefully remove skeletons, then insert the HTML and animate in
    const skeletonCards = container.querySelectorAll('.skeleton-card');
    const doInsert = () => {
      container.innerHTML = html;
      container.querySelectorAll('.player-item').forEach(item => item.classList.add('fade-in'));
      return;
    };

    if (skeletonCards.length) {
      skeletonCards.forEach(card => card.classList.add('fade-out'));
      setTimeout(() => {
        container.querySelectorAll('.loading-skeleton').forEach(item => item.remove());
        doInsert();
      }, 350);
    } else {
      doInsert();
    }
    return;
  }

  ws.addEventListener('message', (ev) => {
    const data = JSON.parse(ev.data);
    if (data.type === 'player_list') renderPlayers(data.players);
    if (data.type === 'player_left') {
      const el = document.querySelector(`#playersList .player-item[data-username="${data.player.username}"] .player-status.online`);
      if (el) {
        el.innerHTML = 'Offline';
        el.style.background = 'rgba(255, 0, 0, 0.3)';
        el.style.color = 'red'
      }
      const count = document.querySelectorAll('#playersList .player-item').length;
      document.querySelector('.player-count').innerText = `Players: ${count-1}/15`;

      let join_username = null;
      if (data.player.username === userinfo.username){
        join_username = "You";
      }else{
        join_username = data.player.username;
      }

      const chatMessages = document.getElementById("chatMessages");
      const messageElement = document.createElement("div");
      messageElement.className = "system-message";
      messageElement.innerText = `${join_username} left the room`;
      chatMessages.appendChild(messageElement);
      chatMessages.scrollTop = chatMessages.scrollHeight;
      self.nplayers --;
      
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

    if (data.type === 'not_found'){
      alert("Not a player. Redirecting to home page.");
      window.location.href = "index.html";
    }
  });

  ws.addEventListener('close', () => console.log('Socket closed'));
  ws.addEventListener('error', (e) => console.error('Socket error', e));

  // ...keep the rest of your admin/chat UI handlers...
// ...existing code...
  // Check if user is admin based on URL parameter
  const isAdmin = userinfo.isAdmin;

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
    if (nplayers > 3){
      ws.send(JSON.stringify(
        {
          "action": "start_game"
        }
      ));
    }else{
      alert('Players must be up to 4')
    }
  })

  // Chat functionality
  const chatInput = document.getElementById("chatInput")
  const sendBtn = document.getElementById("sendBtn")

  function sendMessage() {
    const message = chatInput.value.trim()
    if (message) {
      ws.send(JSON.stringify({
        "action": "message",
        "username": userinfo.username,
        "message": message
      }
      ));
      // addChatMessage("You", message)
      chatInput.value = ""
    };
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
    if (username === 'You'){
      messageElement.className = "you-chat-message"
      messageElement.innerHTML = `<span class="username">${username}:</span> ${message}`
    }else{
      messageElement.className = "chat-message"
      messageElement.innerHTML = `<span class="username">${username}:</span> ${message}`
    }
    chatMessages.appendChild(messageElement)
    chatMessages.scrollTop = chatMessages.scrollHeight
  }
});

