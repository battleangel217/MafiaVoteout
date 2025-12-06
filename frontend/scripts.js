// Basic form interactions - no complex logic
document.addEventListener("DOMContentLoaded", () => {
  const urlParams = new URLSearchParams(window.location.search);
  const roomCode = urlParams.get('code');

  if (roomCode){
    document.getElementById('roomCode').value = roomCode.replace('Room: ', '');
  }
  // Show room code display when create form is submitted
  document.getElementById("createRoomForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("username").value;

    if (username.trim() === '' || username.length < 3){
      document.getElementById('createUsernameError').style.display = "block";
      document.getElementById('createUsernameError').innerText = "Enter a valid username (hint: > 2)";
      return;
    }

    const status = document.getElementById("roomType").value;

    const data = {
      username: username,
      status: status
      // isAdmin: true
    };

    try{
      const response = await fetch('https://mafiavoteout-backend1.onrender.com/api/v1/room/',
        {
          method: "POST",
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify(data)
        });
      
        if(!response.ok){
          if (response.status === 400){
            console.log("Hello world");
            document.getElementById('createUsernameError').style.display = "block";
            document.getElementById('createUsernameError').innerText = "Username already exist";
            return;
          }
          throw new Error('Failed');
        }

        const res = await response.json();

        document.getElementById("roomCodeDisplay").style.display = "block";
        document.getElementById("generatedRoomCode").innerText = res.code;
        localStorage.setItem('userinfo', JSON.stringify(res));

        setTimeout(() => {
          console.log("Fuck you");    
          window.location.href='lobby.html';
        }, 20000);
        
    }catch(error){
      alert("Can't connect to server")
      console.log("Error", error.message);}
  })

  // Auto-uppercase room code input
  document.getElementById("roomCode").addEventListener("input", (e) => {
    e.target.value = e.target.value.toUpperCase()
  })

  // Add visual feedback for form interactions
  const inputs = document.querySelectorAll("input")
  inputs.forEach((input) => {
    input.addEventListener("focus", function () {
      this.parentElement.style.transform = "scale(1.02)"
    })

    input.addEventListener("blur", function () {
      this.parentElement.style.transform = "scale(1)"
    })
  })


  document.getElementById('joinRoomForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('joinUsername').value;
    const code = document.getElementById('roomCode').value;

    if (username.trim() === '' || username.length < 3){
      document.getElementById('joinUsernameError').style.display = "block";
      document.getElementById('joinUsernameError').innerText = "Enter a valid username (hint: > 2)";
      return;
    }

    const data = {
      username:username,
      room:code,
      isAdmin: false
    }

    try{
      const response = await fetch('https://mafiavoteout-backend1.onrender.com/api/v1/player/',
        {
          method: "POST",
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify(data)
        });

        if(!response.ok){
          const err = await response.json();
          if (response.status === 400){
            if (err.username){
              document.getElementById('joinUsernameError').style.display = "block";
              document.getElementById('joinUsernameError').innerText = "Username already taken";
              return;
            }else{
              alert('Server Error');
              return;
            }
          }else if (response.status === 401){
            document.getElementById('roomCodeError').style.display = "block";
            document.getElementById('roomCodeError').innerText = err.message;
            return;
          }else if (response.status === 404){
            document.getElementById('roomCodeError').style.display = "block";
            document.getElementById('roomCodeError').innerText = "Room does not exist";
            return;
          }
          throw new Error("Failed")
        }

        const res = await response.json();
        localStorage.setItem('userinfo', JSON.stringify(res));
        window.location.href='lobby.html';

    }catch(error){
      alert("Can't connect to server")
      console.log("Error", error)
    }
  })


})


