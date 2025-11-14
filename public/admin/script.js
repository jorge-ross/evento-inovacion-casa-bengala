const API_URL =
  "https://evento-inovacion-casa-bengala-production.up.railway.app/api/registrations";

document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const key = document.getElementById("auth-key").value.trim();
  const error = document.getElementById("login-error");

  if (!key) {
    error.textContent = "Por favor, ingresa una clave.";
    return;
  }

  try {
    const res = await fetch(`${API_URL}?key=${key}`);
    if (!res.ok) {
      error.textContent = "Clave incorrecta o no autorizada.";
      return;
    }

    const data = await res.json();
    showTable(data.registrations);
    localStorage.setItem("auth_key", key);
  } catch (err) {
    error.textContent = "Error al conectar con el servidor.";
  }
});

function showTable(registros) {
  document.getElementById("login-section").classList.add("hidden");
  document.getElementById("table-section").classList.remove("hidden");

  const tbody = document.getElementById("table-body");
  tbody.innerHTML = "";

  registros.forEach((r) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${r.name}</td>
      <td>${r.email}</td>
      <td>${r.message}</td>
      <td>${new Date(r.created_at).toLocaleString()}</td>
    `;
    tbody.appendChild(tr);
  });
}

document.getElementById("logout-btn").addEventListener("click", () => {
  localStorage.removeItem("auth_key");
  document.getElementById("table-section").classList.add("hidden");
  document.getElementById("login-section").classList.remove("hidden");
  document.getElementById("auth-key").value = "";
});
