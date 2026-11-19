/* 移动端侧边栏菜单：由 footer 引入 */
(function () {
  "use strict";

  var mobileHeader = document.querySelector(".mobile-header");
  var hamburger = document.querySelector(".hamburger");
  var overlay = document.querySelector(".overlay-menu");

  if (!mobileHeader || !hamburger || !overlay) {
    return;
  }

  overlay.id = overlay.id || "mobile-menu";

  mobileHeader.setAttribute("role", "button");
  mobileHeader.setAttribute("tabindex", "0");
  mobileHeader.setAttribute("aria-controls", overlay.id);
  mobileHeader.setAttribute("aria-expanded", "false");
  mobileHeader.setAttribute("aria-label", "打开导航菜单");
  hamburger.setAttribute("aria-hidden", "true");

  function setOpen(open) {
    hamburger.classList.toggle("cross", open);
    overlay.style.display = open ? "block" : "none";
    overlay.style.width = open ? "100%" : "0%";
    overlay.style.height = open ? "100vh" : "0%";
    mobileHeader.setAttribute("aria-expanded", open ? "true" : "false");
    document.body.style.overflow = open ? "hidden" : "";
  }

  function toggle() {
    setOpen(!hamburger.classList.contains("cross"));
  }

  mobileHeader.addEventListener("click", toggle);
  mobileHeader.addEventListener("keydown", function (event) {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      toggle();
    }
  });

  // 点击菜单中的链接后自动收起
  overlay.addEventListener("click", function (event) {
    if (event.target.closest("a")) {
      setOpen(false);
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      setOpen(false);
    }
  });

  setOpen(false);
})();
