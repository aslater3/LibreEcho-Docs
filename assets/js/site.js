document.documentElement.classList.replace("no-js", "js");

const configuration = {
  productRepository: "https://github.com/aslater3/LibreEcho",
  productIssues: "https://github.com/aslater3/LibreEcho/issues",
};

document.querySelectorAll("[data-repo-link]").forEach((link) => {
  link.href = configuration.productRepository;
});
document.querySelectorAll("[data-issues-link]").forEach((link) => {
  link.href = configuration.productIssues;
});

const toggle = document.querySelector(".menu-toggle");
const nav = document.querySelector(".primary-nav");
const closeMenu = () => {
  if (!toggle || !nav) return;
  nav.classList.remove("open");
  toggle.setAttribute("aria-expanded", "false");
};
if (toggle && nav) {
  toggle.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(open));
  });
  nav.addEventListener("click", (event) => {
    if (event.target.closest("a")) closeMenu();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeMenu();
  });
}
