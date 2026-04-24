// web/static/js/main.js
const API_BASE_URL = "/api";

document.addEventListener("DOMContentLoaded", () => {
  // Corregir Navegación
  const navButtons = document.querySelectorAll(".main-nav .nav-button");
  const sections = document.querySelectorAll(".view"); // Asumiendo que ahora las secciones tienen clase view

  navButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetId = btn.dataset.view + "-view";
      // Scroll suave a la sección
      document.getElementById(targetId).scrollIntoView({ behavior: "smooth" });

      navButtons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
    });
  });

  // Carga de datos
  loadPortfolioData();
  loadETFData();
  loadDividendosData();
  loadMacroNews();
});

function getSignalClass(signal) {
  if (!signal) return "grey";
  const s = signal.toUpperCase();
  if (s.includes("COMPRAR")) return "gold";
  if (s.includes("DCA")) return "orange";
  if (s.includes("ESPERAR") || s.includes("DESCARTAR")) return "red";
  return "grey";
}
