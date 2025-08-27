// On load, check saved theme
window.addEventListener("DOMContentLoaded", function () {
  const toggle = document.getElementById("themeSwitch");
  const isDark = localStorage.getItem("theme") === "dark";

  if (isDark) {
    document.body.classList.add("dark");
    toggle.checked = true;
  }

  toggle.addEventListener("change", function () {
    if (this.checked) {
      document.body.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.body.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  });
});
