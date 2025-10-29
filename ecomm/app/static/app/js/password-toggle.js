// Password Toggle Functionality
function setupPasswordToggles() {
  document
    .querySelectorAll(".password-field-container")
    .forEach((container) => {
      const input = container.querySelector('input[type="password"]');
      const toggle = container.querySelector(".password-toggle");

      if (toggle && input) {
        toggle.addEventListener("click", () => {
          // Toggle password visibility
          const type =
            input.getAttribute("type") === "password" ? "text" : "password";
          input.setAttribute("type", type);

          // Toggle icon
          toggle.innerHTML =
            type === "password"
              ? '<i class="far fa-eye"></i>'
              : '<i class="far fa-eye-slash"></i>';
        });
      }
    });
}

// Setup password toggles when the document is ready
document.addEventListener("DOMContentLoaded", setupPasswordToggles);
