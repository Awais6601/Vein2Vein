document.getElementById("themeToggle").addEventListener("click", () => {
  const html = document.documentElement;
  const currentTheme = html.getAttribute("data-theme");
  html.setAttribute("data-theme", currentTheme === "light" ? "dark" : "light");
  document.body.classList.toggle("bg-white");
  document.body.classList.toggle("bg-gray-900");
  document.body.classList.toggle("text-gray-800");
  document.body.classList.toggle("text-gray-300");
});
