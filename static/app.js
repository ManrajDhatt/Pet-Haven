function showModal(eventId, event = null) {
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }

  const modalElement = document.getElementById(`modal-${eventId}`);
  if (modalElement) {
    modalElement.style.display = "flex";
  } else {
    console.error(`Modal not found for event ID: ${eventId}`);
  }
}

function closeModal(eventId, event = null) {
  const modal = document.getElementById(`modal-${eventId}`);

  // Check if the modal exists
  if (!modal) return;

  // Close modal when clicking on the close button or outside
  if (!event || event.target.classList.contains("modal")) {
    modal.style.display = "none";
  }
}

function toggleDropdown() {
  document.querySelector(".profile-dropdown").classList.toggle("active");
}

// Close dropdown when clicking outside
window.onclick = function (event) {
  if (!event.target.closest(".profile-dropdown")) {
    document.querySelector(".profile-dropdown").classList.remove("active");
  }
};

function redirectToRegister(eventId) {
  window.location.href = `/register_event/${eventId}`;
}

document.addEventListener("DOMContentLoaded", function () {
  // Flash message handling
  setTimeout(function () {
    document.querySelectorAll(".flash-message").forEach(function (msg) {
      msg.style.opacity = "0";
      setTimeout(() => msg.remove(), 500);
    });
  }, 3000);

  // Burger menu handling
  const burger = document.getElementById("burger-menu");
  const sidebar = document.getElementById("sidebar");

  if (burger && sidebar) {
    burger.addEventListener("click", function () {
      sidebar.classList.toggle("show");
    });
  }

  // Add click handlers for all event cards
  document.querySelectorAll(".event-card").forEach((card) => {
    card.addEventListener("click", function (e) {
      const eventId = this.getAttribute("data-event-id");
      if (eventId) {
        showModal(eventId, e);
      }
    });
  });
});

// Registration container toggle
document.addEventListener("DOMContentLoaded", function () {
  const myRegistrationsBtn = document.getElementById("my-registrations");
  if (myRegistrationsBtn) {
    myRegistrationsBtn.addEventListener("click", function () {
      const registeredContainer = document.getElementById(
        "registered-events-container"
      );
      const allEventsContainer = document.getElementById(
        "all-events-container"
      );

      if (registeredContainer) registeredContainer.style.display = "block";
      if (allEventsContainer) allEventsContainer.style.display = "none";
    });
  }
});
