const registerForm = document.querySelector("#register-form");
const loginForm = document.querySelector("#login-form");
const meButton = document.querySelector("#me-button");
const logoutButton = document.querySelector("#logout-button");
const responseOutput = document.querySelector("#response-output");
const statusBadge = document.querySelector("#status-badge");
const tokenOutput = document.querySelector("#token-output");

const ACCESS_TOKEN_KEY = "playerbase.accessToken";

function getAccessToken() {
  return window.localStorage.getItem(ACCESS_TOKEN_KEY) || "";
}

function setAccessToken(token) {
  if (token) {
    window.localStorage.setItem(ACCESS_TOKEN_KEY, token);
  } else {
    window.localStorage.removeItem(ACCESS_TOKEN_KEY);
  }
  tokenOutput.textContent = token || "None";
}

function renderResponse(label, payload) {
  statusBadge.textContent = label;
  responseOutput.textContent = JSON.stringify(payload, null, 2);
}

async function apiFetch(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  const token = getAccessToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(path, {
    ...options,
    headers,
  });

  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || "Request failed.");
  }
  return payload;
}

registerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(registerForm);
  const payload = Object.fromEntries(formData.entries());

  try {
    const data = await apiFetch("/api/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    setAccessToken(data.tokens.access_token);
    renderResponse("Registered", data);
  } catch (error) {
    renderResponse("Error", { error: error.message });
  }
});

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(loginForm);
  const payload = Object.fromEntries(formData.entries());

  try {
    const data = await apiFetch("/api/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    setAccessToken(data.tokens.access_token);
    renderResponse("Logged in", data);
  } catch (error) {
    renderResponse("Error", { error: error.message });
  }
});

meButton.addEventListener("click", async () => {
  try {
    const data = await apiFetch("/api/me");
    renderResponse("Current user", data);
  } catch (error) {
    renderResponse("Error", { error: error.message });
  }
});

logoutButton.addEventListener("click", async () => {
  try {
    const data = await apiFetch("/api/logout", {
      method: "POST",
      body: JSON.stringify({}),
    });
    setAccessToken("");
    renderResponse("Logged out", data);
  } catch (error) {
    renderResponse("Error", { error: error.message });
  }
});

setAccessToken(getAccessToken());
