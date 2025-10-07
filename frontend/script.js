;(() => {
  // Configure your backend URL here
  const API_BASE = window.API_BASE || "http://localhost:8000"

  const qs = (sel, root = document) => root.querySelector(sel)
  const qsa = (sel, root = document) => Array.from(root.querySelectorAll(sel))

  // Footer year
  qs("#year").textContent = String(new Date().getFullYear())

  // Fetch helpers
  async function getJSON(path) {
    try {
      const res = await fetch(`${API_BASE}${path}`, { credentials: "omit" })
      if (!res.ok) throw new Error(`GET ${path} failed`)
      return await res.json()
    } catch (err) {
      console.warn("[v0] GET error:", err.message)
      return null
    }
  }

  async function postJSON(path, payload) {
    try {
      const res = await fetch(`${API_BASE}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) throw new Error(data?.message || `POST ${path} failed`)
      return data
    } catch (err) {
      console.warn("[v0] POST error:", err.message)
      throw err
    }
  }

  // Populate schemes
  async function populateSchemes() {
    const grid = qs("#schemes-grid")
    const data = await getJSON("/api/schemes")
    if (!data || !Array.isArray(data)) return // keep static fallback
    grid.innerHTML = ""
    data.forEach((s) => {
      const a = document.createElement("article")
      a.className = "card"
      a.innerHTML = `
        <h3>${escapeHTML(s.title)}</h3>
        <p>${escapeHTML(s.description)}</p>
        ${s.link ? `<p><a href="${s.link}" target="_blank" rel="noopener">Learn more →</a></p>` : ""}
      `
      grid.appendChild(a)
    })
  }

  // Populate products
  async function populateProducts() {
    const grid = qs("#products-grid")
    const data = await getJSON("/api/products")
    if (!data || !Array.isArray(data)) return // keep static fallback
    grid.innerHTML = ""
    data.forEach((p) => {
      const article = document.createElement("article")
      article.className = "card"
      article.innerHTML = `
        <div class="product">
          <div class="product-media" role="img" aria-label="${escapeHTML(p.title)} image placeholder" style=""></div>
          <div class="product-body">
            <h3>${escapeHTML(p.title)}</h3>
            <p class="seller">Seller: ${escapeHTML(p.seller || "Unknown")}</p>
            ${p.price != null ? `<p class="price">₹${escapeHTML(String(p.price))}</p>` : ""}
          </div>
        </div>
      `
      grid.appendChild(article)
    })
  }

  // Forms
  function wireForms() {
    const contactForm = qs("#contact-form")
    const contactResp = qs("#contact-response")
    if (contactForm) {
      contactForm.addEventListener("submit", async (e) => {
        e.preventDefault()
        const fd = new FormData(contactForm)
        const payload = {
          name: String(fd.get("name") || "").trim(),
          email: String(fd.get("email") || "").trim(),
          message: String(fd.get("message") || "").trim(),
        }
        contactResp.textContent = "Sending..."
        try {
          await postJSON("/api/contact", payload)
          contactResp.textContent = "Thanks! Our team will reach out shortly."
          contactForm.reset()
        } catch (err) {
          contactResp.textContent = "Something went wrong. Please try again."
        }
      })
    }

    const subForm = qs("#subscribe-form")
    const subResp = qs("#subscribe-response")
    if (subForm) {
      subForm.addEventListener("submit", async (e) => {
        e.preventDefault()
        const fd = new FormData(subForm)
        const payload = { email: String(fd.get("email") || "").trim() }
        subResp.textContent = "Submitting..."
        try {
          await postJSON("/api/subscribe", payload)
          subResp.textContent = "You are subscribed. We will guide you soon!"
          subForm.reset()
        } catch (err) {
          subResp.textContent = "Unable to subscribe. Please try again."
        }
      })
    }
  }

  // Safe HTML
  function escapeHTML(str) {
    return str.replace(
      /[&<>"']/g,
      (m) =>
        ({
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#39;",
        })[m],
    )
  }

  document.addEventListener("DOMContentLoaded", () => {
    populateSchemes()
    populateProducts()
    wireForms()
  })
})()
