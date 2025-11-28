document.addEventListener("DOMContentLoaded", () => {
  userinfo = JSON.parse(localStorage.getItem('userinfo') || '{}');
  code = userinfo.room || userinfo.code;
  self.isvoted = localStorage.getItem('isVoted') || false;
  self.isVoted = (str === "true");  
  self.votee = localStorage.getItem('votee') || null;
  document.querySelector('.room-code').innerText = `Room: ${code}`;

  // let timeLeft = 20;
  // const timerElement = document.getElementById("timer");
  const ws = new WebSocket(`ws://127.0.0.1:8000/ws/voting/${code}/`);
  // console.log(ws.send(JSON.stringify({ action: 'join', username: userinfo.username})));

  ws.addEventListener('open', () => {
    ws.send(JSON.stringify({ action: 'join', username: userinfo.username}));
    ws.send(JSON.stringify({}))
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
            <button class="vote-btn" disabled>Vote</button>
          </div>`;
      }else{
        container.innerHTML += `
          <div class="player-item" data-username="${item.username}">
            <div class="player-info">
              <span class="player-name">${item.username}</span>
            </div>
            <button class="vote-btn" disabled>Vote</button>
          </div>`;
      }
    });


    document.querySelectorAll(".vote-btn").forEach((button) => {
    console.log('yoi');
    button.addEventListener("click", function () {
      if (!this.disabled) {
        // Reset all buttons
        document.querySelectorAll(".vote-btn").forEach((btn) => {
          btn.classList.remove("voted");
          btn.textContent = "Vote";
          btn.disabled = true;
        })

        // Mark this button as voted
        this.classList.add("voted");
        this.textContent = "Voted";
        this.disabled = true;
        

        // Add chat message
        // const playerName = this.closest(".player-item").querySelector(".player-name").textContent;
        const username = this.closest(".player-item").dataset.username;
        self.isVoted = true;
        localStorage.setItem('isVoted', self.isVoted);
        localStorage.setItem('votee', username);
        ws.send(JSON.stringify(
          {
            "action": "vote",
            "votee": username
          }
        ));
      }
    })
    })

    return;
  }

  function renderVote(list){
      const container = document.getElementById('resultsList');
      container.innerHTML = '';

      list.forEach(item => {
        if (userinfo.username === item.username){
          container.innerHTML += `
            <div class="result-item">
                <span class="result-name">${item.username} (You)</span>
                <span class="result-votes">${item.vote} votes</span>
            </div>`;
        }else{
          container.innerHTML += `
            <div class="result-item">
                <span class="result-name">${item.username}</span>
                <span class="result-votes">${item.vote} votes</span>
            </div>`;
        }
        console.log(item);
        
      });
  }

  ws.addEventListener('message', (ev) => {
    const data = JSON.parse(ev.data);
    const timerElement = document.getElementById("timer");
    const timerContainer = document.getElementById("timerContainer")
    if (data.type === 'player_list'){
      renderPlayers(data.players); 
      renderVote(data.players);
    }
    if (data.type === 'player_left') {
      const el = document.querySelector(`#playersList .player-item[data-username="${data.player.username}"]`);
      if (el) el.remove();
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

    if (data.type === 'timer'){
      let timeLeft = data.time_left;
      timerElement.textContent = timeLeft;
      if (!self.isVoted){
        console.log("hello")
        document.querySelectorAll('.vote-btn').forEach((btn) => {
          btn.disabled = false;
        })
      }else{
        console.log("did ts work")
        document.querySelectorAll('.vote-btn').forEach((btn) => {
          btn.disabled = true;
        });
        
        const playerDiv = document.querySelector(`.player-item[data-username="${self.votee}"]`);
        if (playerDiv) {
            const voteBtn = playerDiv.querySelector(".vote-btn");
            if (voteBtn) voteBtn.classList.add("voted");
        }
      }
      // }else {
      //   const layout = localStorage.getItem('votelayout')
      //   document.querySelector('.players-list').innerHTML = layout;
      // }

    // Add visual warnings
      if (timeLeft <= 5) {
        timerElement.className = "timer critical";
        // keep the container class as timer-container and add a modifier
        timerContainer.className = "timer-container critical";
      } else if (timeLeft <= 10) {
        timerElement.className = "timer warning";
        timerContainer.className = "timer-container warning";
      } else if (timeLeft <= 60){
        timerElement.className = "timer first warning";
        // use first + warning modifier classes on the container (no .timer class)
        timerContainer.className = "timer-container first warning";
      }
    }

    if (data.type === 'start_voting'){
      const chatMessages = document.getElementById("chatMessages");
      const messageElement = document.createElement("div");
      messageElement.className = "system-message";
      messageElement.innerText = `Voting has Started!`;
      chatMessages.appendChild(messageElement);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    if (data.type === 'vote_recorded'){
      let join_username = null;
      if (data.voter === userinfo.username){
        join_username = "You";
      }else{
        join_username = data.username;
      }

      const chatMessages = document.getElementById("chatMessages");
      const messageElement = document.createElement("div");
      messageElement.className = "system-message";
      messageElement.innerText = `${join_username} voted for ${data.votee}`;
      chatMessages.appendChild(messageElement);
      chatMessages.scrollTop = chatMessages.scrollHeight;

    }

    if (data.type === 'timer_finished'){
      timerElement.textContent = 120;
      timerElement.className = "timer";
      timerContainer.className = "timer-container";
      document.getElementById("voteResults").style.display = "block";
      document.getElementById("eliminationResult").style.display = "block";

    }

    if (data.type === 'start_game'){
      window.location.href = "voting.html";
    }

    if (data.type === 'not_found'){
      alert("Not a player/Room. Redirecting to home page.");
      window.location.href = "index.html";
    }

    if (data.type === 'room_started'){
      alert("Game has not started. Redirecting to lobby.");
      window.location.href = "lobby.html";
    }
  })
  ws.addEventListener('close', () => console.log('Socket closed'));
  ws.addEventListener('error', (e) => console.error('Socket error', e));

  // Simple timer countdown for demo
  // const timerInterval = setInterval(() => {
  //   timeLeft--
    // timerElement.textContent = timeLeft

    // // Add visual warnings
    // if (timeLeft <= 5) {
    //   timerElement.className = "timer critical"
    // } else if (timeLeft <= 10) {
    //   timerElement.className = "timer warning"
    // }

    // if (timeLeft <= 0) {
    //   clearInterval(timerInterval)
    //   // Show results sections
    //   document.getElementById("voteResults").style.display = "block"
    //   setTimeout(() => {
        // document.getElementById("eliminationResult").style.display = "block"
    //   }, 2000)
    // }
  // }, 1000)

  // Vote button interactions
  // document.querySelectorAll(".vote-btn").forEach((button) => {
  //   console.log('yoi');
  //   button.addEventListener("click", function () {
  //     if (!this.disabled) {
  //       // Reset all buttons
  //       document.querySelectorAll(".vote-btn").forEach((btn) => {
  //         btn.classList.remove("voted");
  //         btn.textContent = "Vote";
  //         btn.disabled = false;
  //       })

  //       // Mark this button as voted
  //       this.classList.add("voted");
  //       this.textContent = "Voted";
  //       this.disabled = true;

  //       // Add chat message
  //       const playerName = this.closest(".player-item").querySelector(".player-name").textContent;
  //       addChatMessage("You", `voted for ${playerName.replace(" (You)", "")}`);
  //     }
  //   })
  // })

  // Chat functionality
  const chatInput = document.getElementById("chatInput");
  const sendBtn = document.getElementById("sendBtn");

  function sendMessage() {
    const message = chatInput.value.trim();
    if (message) {
      ws.send(JSON.stringify(
        {
          "action": "message",
          "username": userinfo.username,
          "message": message
        }
      ));
      chatInput.value = ""
    };
  }

  sendBtn.addEventListener("click", sendMessage);
  chatInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      sendMessage();
    }
  })

  // Next round button
  document.getElementById("nextRoundBtn").addEventListener("click", () => {
    document.getElementById("voteResults").style.display = "none";
    document.getElementById("eliminationResult").style.display = "none";
    ws.send(JSON.stringify({
      "action":"start_timer"
    }))
  })

  if (userinfo.isAdmin){
    document.getElementById("eliminationResult").style.display = 'block';
    document.getElementById("nextRoundBtn").style.display = "block";
  }else{
    document.getElementById("eliminationResult").style.display = 'none';
    document.getElementById("nextRoundBtn").style.display = "none";
  }

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
      console.log("mffff")
      chatMessages.appendChild(messageElement)
      chatMessages.scrollTop = chatMessages.scrollHeight
  }
});