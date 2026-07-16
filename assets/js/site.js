const configuration = {
  repository: "https://github.com/YOUR-USERNAME/libreecho",
};

document.querySelectorAll("[data-repo-link]").forEach((link) => {
  link.href = configuration.repository;
});
document.querySelectorAll("[data-issues-link]").forEach((link) => {
  link.href = `${configuration.repository}/issues`;
});

const toggle = document.querySelector(".menu-toggle");
const nav = document.querySelector(".primary-nav");
if (toggle && nav) {
  toggle.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(open));
  });
  nav.addEventListener("click", () => {
    nav.classList.remove("open");
    toggle.setAttribute("aria-expanded", "false");
  });
}
