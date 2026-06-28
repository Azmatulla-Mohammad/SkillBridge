document.addEventListener("DOMContentLoaded", () => {
  if (window.lucide && typeof window.lucide.createIcons === "function") {
    window.lucide.createIcons();
  }

  const sidebar = document.getElementById("sidebar");
  const toggle = document.querySelector("[data-toggle-sidebar]");
  if (sidebar && toggle) {
    toggle.addEventListener("click", () => {
      sidebar.classList.toggle("open");
    });
  }

  const mobileNav = document.getElementById("mobile-nav");
  const mobileNavToggle = document.querySelector("[data-toggle-mobile-nav]");
  if (mobileNav && mobileNavToggle) {
    mobileNavToggle.addEventListener("click", () => {
      mobileNav.classList.toggle("open");
    });
    mobileNav.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => mobileNav.classList.remove("open"));
    });
  }

  document.querySelectorAll("[data-toggle-password]").forEach((toggleButton) => {
    const passwordField = toggleButton.closest(".password-field");
    const input = passwordField ? passwordField.querySelector("input") : null;
    if (!input) {
      return;
    }

    toggleButton.addEventListener("click", () => {
      const shouldShow = input.type === "password";
      input.type = shouldShow ? "text" : "password";
      toggleButton.setAttribute("aria-pressed", String(shouldShow));
      toggleButton.setAttribute("aria-label", shouldShow ? "Hide password" : "Show password");
      const icon = toggleButton.querySelector("i");
      if (icon) {
        icon.setAttribute("data-lucide", shouldShow ? "eye-off" : "eye");
        if (window.lucide && typeof window.lucide.createIcons === "function") {
          window.lucide.createIcons();
        }
      }
    });
  });

  document.querySelectorAll("label:not(.checkbox)").forEach((label) => {
    const field = label.querySelector("input, textarea, select");
    if (!field) {
      return;
    }
    const syncValueState = () => {
      label.classList.toggle("has-value", Boolean(field.value));
    };
    syncValueState();
    field.addEventListener("input", syncValueState);
    field.addEventListener("change", syncValueState);
  });

  document
    .querySelectorAll(".button, button[type='submit']")
    .forEach((button) => {
      button.addEventListener("click", (event) => {
        const rect = button.getBoundingClientRect();
        const ripple = document.createElement("span");
        const size = Math.max(rect.width, rect.height);
        ripple.className = "ripple";
        ripple.style.width = `${size}px`;
        ripple.style.height = `${size}px`;
        ripple.style.left = `${event.clientX - rect.left - size / 2}px`;
        ripple.style.top = `${event.clientY - rect.top - size / 2}px`;
        button.appendChild(ripple);
        window.setTimeout(() => ripple.remove(), 550);
      });
    });

  document.querySelectorAll("[data-confirm]").forEach((element) => {
    element.addEventListener("click", (event) => {
      const message = element.getAttribute("data-confirm") || "Are you sure?";
      if (!window.confirm(message)) {
        event.preventDefault();
      }
    });
  });

  window.setTimeout(() => {
    document.querySelectorAll(".flash").forEach((flash) => {
      flash.style.opacity = "0";
      flash.style.transform = "translateY(-8px)";
      window.setTimeout(() => flash.remove(), 250);
    });
  }, 4500);

  // Admin: One-time credentials modal
  const modalBackdrop = document.getElementById("created-user-modal-backdrop");
  const modal = document.getElementById("created-user-modal");
  const tempPasswordEl = document.getElementById("created-user-temp-password");
  const copyBtn = document.getElementById("created-user-copy-credentials");

  const closeModal = () => {
    if (modal) modal.style.display = "none";
    if (modalBackdrop) modalBackdrop.style.display = "none";

    // Remove temp password from DOM immediately.
    if (tempPasswordEl) tempPasswordEl.textContent = "";
    const cloned = copyBtn && copyBtn.dataset ? copyBtn.dataset : null;
    // Ensure no accidental persistence in JS memory
    if (copyBtn) {
      copyBtn.dataset.tempPassword = "";
    }
  };

  if (modal && tempPasswordEl) {
    const closeBtn = document.getElementById("created-user-modal-close");
    const closeX = document.getElementById("created-user-modal-close-x");

    if (closeBtn) closeBtn.addEventListener("click", closeModal);
    if (closeX) closeX.addEventListener("click", closeModal);
    if (modalBackdrop) modalBackdrop.addEventListener("click", closeModal);

    if (copyBtn) {
      // Don't store password in dataset; read from DOM on click.
      copyBtn.addEventListener("click", async () => {
        const emailEl = document.getElementById("created-user-email");
        const temp = tempPasswordEl.textContent;
        const email = emailEl ? emailEl.textContent : "";
        const credentials = `Email: ${email}\nTemporary Password: ${temp}`;
        try {
          await navigator.clipboard.writeText(credentials);
          copyBtn.textContent = "Copied!";
          window.setTimeout(() => (copyBtn.textContent = "Copy Credentials"), 1400);
        } catch (e) {
          alert("Copy failed. Please copy the credentials manually.");
        }
      });
    }

    // Close on escape
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closeModal();
    });
  }
});
