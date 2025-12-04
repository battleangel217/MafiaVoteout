document.addEventListener("DOMContentLoaded", async () => {
  const searchInput = document.getElementById("searchInput")
  // const filterType = document.getElementById("filterType")
  const roomsGrid = document.getElementById("roomsGrid")
  const emptyState = document.getElementById("emptyState")


  try{
    const loadingSkeleton = roomsGrid.querySelectorAll(".loading-skeleton");
    const response = await fetch('https://mafiavoteout-backend.onrender.com/api/v1/room/all',
      {
        method: "GET",
        headers: {"Content-Type": "application/json"}
      }
    )

    if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
    }

    const res = await response.json();
    loadingSkeleton.forEach((item) => {
      item.remove();
    })
    const rooms = document.querySelector('.rooms-grid')

    res.forEach((item) => {
      rooms.innerHTML += `
        <div class="room-card">
            <div class="room-header">
                <h3>Room: ${item.code}</h3>
                <span class="room-badge public">Public</span>
            </div>
            <div class="room-info">
                <p><strong>Admin:</strong> ${item.username}</p>
                <p><strong>Players:</strong> ${item.player_count}/8</p>
                <p><strong>Status:</strong> Waiting for players</p>
            </div>
            <button class="btn-join-room" data-code="${item.code}">Join Room</button>
        </div>`;
    });

    document.querySelectorAll(".btn-join-room").forEach((btn) => {
      btn.addEventListener("click", function() {
        const code = this.getAttribute('data-code');
        window.location.href = `index.html?code=${code}`;
      })
    })



  }catch(error){
    alert("can't connect to server");
    console.log("Error", error);
  }


  // Filter and search functionality
  function filterRooms() {
    const searchTerm = searchInput.value.toLowerCase()
    // const selectedType = filterType.value

    const roomCards = roomsGrid.querySelectorAll(".room-card")
    let visibleCount = 0

    roomCards.forEach((card) => {
      const roomCode = card.querySelector("h3").textContent.toLowerCase()
      const roomType = card.querySelector(".room-badge").classList.contains("public") ? "public" : "private"

      const matchesSearch = roomCode.includes(searchTerm) || card.textContent.toLowerCase().includes(searchTerm)
      // const matchesType = !selectedType || roomType === selectedType

      if (matchesSearch) {
        card.style.display = "block"
        visibleCount++
      } else {
        card.style.display = "none"
      }
    })

    emptyState.style.display = visibleCount === 0 ? "block" : "none"
  }

  searchInput.addEventListener("input", filterRooms)
  // filterType.addEventListener("change", filterRooms)
})
