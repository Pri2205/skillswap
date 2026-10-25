// ============ 1. SHOW / HIDE PASSWORD ============
document.querySelectorAll(".pw-toggle").forEach(function (btn) {
  btn.addEventListener("click", function () {
    const input = document.getElementById(btn.dataset.target);
    const show = input.type === "password";
    input.type = show ? "text" : "password";
    btn.textContent = show ? "Hide" : "Show";
  });
});


// ============ 2. SHOW OR CLEAR AN ERROR UNDER A FIELD ============
function setError(input, message) {
  const field = input.closest(".field");
  field.classList.toggle("invalid", message !== "");
  field.querySelector(".field-error").textContent = message;
}


// ============ 3. FORGOT PASSWORD (coming soon) ============
const forgot = document.getElementById("forgotLink");
if (forgot) {
  forgot.addEventListener("click", function (event) {
    event.preventDefault();
    document.getElementById("authMsg").textContent =
      "Password reset is coming soon. For now, email skillswap.helpdesk@gmail.com.";
  });
}


// ============ 4. SIGN UP CHECKS ============
const registerForm = document.getElementById("registerForm");

if (registerForm) {
  const nameInput = document.getElementById("name");
  const emailInput = document.getElementById("email");
  const phoneInput = document.getElementById("phone");
  const passwordInput = document.getElementById("password");
  const confirmInput = document.getElementById("confirm");

  registerForm.addEventListener("submit", function (event) {
    let ok = true;

    if (nameInput.value.trim().length < 2) {
      setError(nameInput, "Please enter your full name.");
      ok = false;
    } else {
      setError(nameInput, "");
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailInput.value.trim())) {
      setError(emailInput, "Please enter a valid email.");
      ok = false;
    } else {
      setError(emailInput, "");
    }

    // 10 digits, starting with 6, 7, 8 or 9
    if (!/^[6-9]\d{9}$/.test(phoneInput.value.trim())) {
      setError(phoneInput, "Enter a 10-digit mobile number.");
      ok = false;
    } else {
      setError(phoneInput, "");
    }

    if (passwordInput.value.length < 8) {
      setError(passwordInput, "Use at least 8 characters.");
      ok = false;
    } else {
      setError(passwordInput, "");
    }

    if (confirmInput.value !== passwordInput.value) {
      setError(confirmInput, "Passwords do not match.");
      ok = false;
    } else {
      setError(confirmInput, "");
    }

    if (!ok) {
      event.preventDefault();      // stop the form from being sent
    }
  });
}