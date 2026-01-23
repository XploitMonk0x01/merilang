// Tab switching functionality
function initTabs() {
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".example-tab");

  tabButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const targetTab = button.dataset.tab;

      // Remove active class from all buttons and tabs
      tabButtons.forEach((btn) => btn.classList.remove("active"));
      tabContents.forEach((tab) => tab.classList.remove("active"));

      // Add active class to clicked button and corresponding tab
      button.classList.add("active");
      document.getElementById(targetTab).classList.add("active");
    });
  });
}

// Smooth scrolling for navigation links
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      const href = this.getAttribute("href");
      if (href !== "#") {
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
          target.scrollIntoView({
            behavior: "smooth",
            block: "start",
          });
        }
      }
    });
  });
}

// Syntax highlighting (basic implementation)
function highlightCode() {
  const codeBlocks = document.querySelectorAll("pre code");

  codeBlocks.forEach((block) => {
    let html = block.innerHTML;

    // Define DesiLang keywords
    const keywords = [
      "likho",
      "maan",
      "agar",
      "warna",
      "agarlena",
      "jab_tak",
      "bar_bar",
      "ruk",
      "age_badho",
      "kaam",
      "wapas",
      "class",
      "badhaao",
      "naya",
      "yeh",
      "upar",
      "koshish",
      "pakdo",
      "fenko",
      "akhir",
      "sach",
      "jhoot",
    ];

    // Highlight keywords
    keywords.forEach((keyword) => {
      const regex = new RegExp(`\\b(${keyword})\\b`, "g");
      html = html.replace(regex, '<span class="keyword">$1</span>');
    });

    // Highlight strings
    html = html.replace(/"([^"]*)"/g, '<span class="string">"$1"</span>');
    html = html.replace(/'([^']*)'/g, "<span class=\"string\">'$1'</span>");

    // Highlight comments
    html = html.replace(/\/\/(.*?)$/gm, '<span class="comment">//$1</span>');

    // Highlight numbers
    html = html.replace(/\b(\d+)\b/g, '<span class="number">$1</span>');

    block.innerHTML = html;
  });
}

// Add copy buttons to code blocks
function addCopyButtons() {
  const codeBlocks = document.querySelectorAll("pre");

  codeBlocks.forEach((block) => {
    const button = document.createElement("button");
    button.className = "copy-btn";
    button.textContent = "📋 Copy";
    button.style.cssText = `
            position: absolute;
            top: 0.5rem;
            right: 0.5rem;
            padding: 0.5rem 1rem;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.875rem;
            opacity: 0;
            transition: opacity 0.3s;
        `;

    block.style.position = "relative";

    block.addEventListener("mouseenter", () => {
      button.style.opacity = "1";
    });

    block.addEventListener("mouseleave", () => {
      button.style.opacity = "0";
    });

    button.addEventListener("click", () => {
      const code = block.querySelector("code");
      const text = code ? code.textContent : block.textContent;

      navigator.clipboard
        .writeText(text)
        .then(() => {
          button.textContent = "✓ Copied!";
          setTimeout(() => {
            button.textContent = "📋 Copy";
          }, 2000);
        })
        .catch((err) => {
          console.error("Failed to copy:", err);
        });
    });

    block.appendChild(button);
  });
}

// Mobile menu toggle
function initMobileMenu() {
  const nav = document.querySelector(".nav-links");
  const burger = document.createElement("div");
  burger.className = "burger-menu";
  burger.innerHTML = "☰";
  burger.style.cssText = `
        display: none;
        font-size: 1.5rem;
        cursor: pointer;
        padding: 0.5rem;
        @media (max-width: 768px) {
            display: block;
        }
    `;

  // Only add burger menu on mobile
  if (window.innerWidth <= 768) {
    burger.style.display = "block";
    document.querySelector(".navbar .container").appendChild(burger);

    burger.addEventListener("click", () => {
      nav.style.display = nav.style.display === "flex" ? "none" : "flex";
      nav.style.flexDirection = "column";
      nav.style.position = "absolute";
      nav.style.top = "100%";
      nav.style.left = "0";
      nav.style.right = "0";
      nav.style.background = "white";
      nav.style.padding = "1rem";
      nav.style.boxShadow = "0 4px 6px rgba(0,0,0,0.1)";
    });
  }
}

// Scroll animation
function initScrollAnimation() {
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -100px 0px",
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = "1";
        entry.target.style.transform = "translateY(0)";
      }
    });
  }, observerOptions);

  // Animate feature cards
  document
    .querySelectorAll(".feature-card, .doc-card, .quickstart-step")
    .forEach((el) => {
      el.style.opacity = "0";
      el.style.transform = "translateY(20px)";
      el.style.transition = "opacity 0.6s ease, transform 0.6s ease";
      observer.observe(el);
    });
}

// Initialize everything when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initSmoothScroll();
  highlightCode();
  addCopyButtons();
  initMobileMenu();
  initScrollAnimation();

  // Set first tab as active by default
  const firstTab = document.querySelector(".tab-btn");
  if (firstTab) {
    firstTab.click();
  }
});

// Add active state to current navigation link
window.addEventListener("scroll", () => {
  const sections = document.querySelectorAll("section[id]");
  const navLinks = document.querySelectorAll(".nav-links a");

  let current = "";
  sections.forEach((section) => {
    const sectionTop = section.offsetTop;
    const sectionHeight = section.clientHeight;
    if (window.pageYOffset >= sectionTop - 200) {
      current = section.getAttribute("id");
    }
  });

  navLinks.forEach((link) => {
    link.classList.remove("active");
    if (link.getAttribute("href") === `#${current}`) {
      link.classList.add("active");
    }
  });
});
