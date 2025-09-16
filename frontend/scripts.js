// Basic form interactions - no complex logic
document.addEventListener("DOMContentLoaded", () => {
  // Show room code display when create form is submitted
  document.getElementById("createRoomForm").addEventListener("submit", (e) => {
    e.preventDefault()
    document.getElementById("roomCodeDisplay").style.display = "block";

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
})


