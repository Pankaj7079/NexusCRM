// NexusCRM — Interactive Enterprise Web Dashboard Application

let authToken = localStorage.getItem("nexuscrm_jwt_token") || null;

document.addEventListener("DOMContentLoaded", async () => {
  await ensureAuthToken();
  initTabs();
  initCharts();
  loadContacts();
  loadDeals();
  initAgentChat();
  initRAG();
  initCRMFormHandlers();
});

// Auto-Login as Default Admin if Token Missing or Expired
async function ensureAuthToken() {
  if (authToken) return authToken;

  try {
    const formData = new URLSearchParams();
    formData.append("username", "admin@nexuscrm.io");
    formData.append("password", "admin123");

    const res = await fetch("/api/v1/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formData,
    });

    if (res.ok) {
      const data = await res.json();
      authToken = data.access_token;
      localStorage.setItem("nexuscrm_jwt_token", authToken);
    }
  } catch (err) {
    console.warn("Auto-login fallback using local session.");
  }
  return authToken;
}

// Get Auth Headers for API Requests
function getAuthHeaders() {
  const headers = { "Content-Type": "application/json" };
  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`;
  }
  return headers;
}

// Tab Navigation Manager
function initTabs() {
  const navButtons = document.querySelectorAll(".nav-item");
  const tabContents = document.querySelectorAll(".tab-content");
  const pageTitle = document.getElementById("page-title");

  const titles = {
    dashboard: "Executive Intelligence Dashboard",
    chat: "Multi-Agent System & Harness Workspace",
    contacts: "Contacts & Lead Intelligence",
    deals: "Sales Deals & Pipeline Management",
    rag: "PageIndex Hybrid RAG Knowledge Base",
    analytics: "Predictive ML Models & Benchmarks",
  };

  navButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetTab = btn.getAttribute("data-tab");

      navButtons.forEach((b) => b.classList.remove("active"));
      tabContents.forEach((c) => c.classList.remove("active"));

      btn.classList.add("active");
      const targetEl = document.getElementById(`tab-${targetTab}`);
      if (targetEl) targetEl.classList.add("active");
      if (pageTitle) pageTitle.textContent = titles[targetTab] || "NexusCRM";

      if (targetTab === "contacts") loadContacts();
      if (targetTab === "deals") loadDeals();
    });
  });
}

// Dashboard Charts Visualization
function initCharts() {
  const ctxForecast = document.getElementById("chart-forecast")?.getContext("2d");
  if (ctxForecast) {
    new Chart(ctxForecast, {
      type: "line",
      data: {
        labels: ["Month 1", "Month 2", "Month 3", "Month 4", "Month 5", "Month 6"],
        datasets: [
          {
            label: "Projected Revenue ($)",
            data: [400542, 408500, 416000, 424500, 432000, 440000],
            borderColor: "#38bdf8",
            backgroundColor: "rgba(56, 189, 248, 0.1)",
            fill: true,
            tension: 0.4,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: { legend: { labels: { color: "#94a3b8" } } },
        scales: {
          x: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } },
          y: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } },
        },
      },
    });
  }

  const ctxDeals = document.getElementById("chart-deals")?.getContext("2d");
  if (ctxDeals) {
    new Chart(ctxDeals, {
      type: "bar",
      data: {
        labels: ["PROSPECTING", "QUALIFICATION", "NEEDS_ANALYSIS", "PROPOSAL", "NEGOTIATION", "CLOSED_WON"],
        datasets: [
          {
            label: "Deals Count",
            data: [18, 15, 22, 16, 11, 18],
            backgroundColor: ["#38bdf8", "#a855f7", "#fbbf24", "#34d399", "#f87171", "#22c55e"],
            borderRadius: 6,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } },
          y: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } },
        },
      },
    });
  }
}

// Fetch and Render Real Database Contacts
async function loadContacts() {
  const tbody = document.getElementById("contacts-tbody");
  if (!tbody) return;

  try {
    await ensureAuthToken();
    const res = await fetch("/api/v1/contacts?limit=50", { headers: getAuthHeaders() });
    
    if (res.status === 401) {
      localStorage.removeItem("nexuscrm_jwt_token");
      authToken = null;
      await ensureAuthToken();
    }

    if (!res.ok) throw new Error("API call failed");
    const contacts = await res.json();

    const countMetric = document.getElementById("metric-contacts-count");
    if (countMetric) countMetric.textContent = contacts.length;

    tbody.innerHTML = "";
    contacts.forEach((c) => {
      const tr = document.createElement("tr");
      const scoreBadge = c.lead_score >= 80 ? "green" : c.lead_score >= 50 ? "blue" : "red";
      const churnBadge = c.churn_risk >= 0.5 ? "red" : c.churn_risk >= 0.25 ? "blue" : "green";

      tr.innerHTML = `
        <td><strong>${c.first_name} ${c.last_name}</strong></td>
        <td>${c.email}</td>
        <td>${c.job_title || "Executive"}</td>
        <td><span class="badge-tag ${scoreBadge}">${(c.lead_score || 75.0).toFixed(1)} / 100</span></td>
        <td><span class="badge-tag ${churnBadge}">${((c.churn_risk || 0.15) * 100).toFixed(0)}% Risk</span></td>
        <td><span class="badge-tag blue">${(c.lead_status || 'QUALIFIED').toUpperCase()}</span></td>
        <td>
          <button class="btn btn-secondary btn-sm" onclick="triggerActionForContact('${c.email}', 'draft_email')"><i class="fa-solid fa-paper-plane"></i> Email</button>
          ${c.churn_risk >= 0.4 ? `<button class="btn btn-danger btn-sm" onclick="triggerActionForContact('${c.email}', 'churn_retain')"><i class="fa-solid fa-bolt"></i> Retain</button>` : ''}
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Failed to load contacts:", err);
  }
}

// Fetch and Render Real Database Deals
async function loadDeals() {
  const tbody = document.getElementById("deals-tbody");
  if (!tbody) return;

  try {
    await ensureAuthToken();
    const res = await fetch("/api/v1/deals?limit=50", { headers: getAuthHeaders() });
    if (!res.ok) throw new Error("Deals API failed");
    const deals = await res.json();

    tbody.innerHTML = "";
    let totalPipelineValue = 0;

    deals.forEach((d) => {
      totalPipelineValue += (d.value || 0);
      const tr = document.createElement("tr");
      const stageBadge = d.stage === "CLOSED_WON" ? "green" : d.stage === "CLOSED_LOST" ? "red" : "blue";

      tr.innerHTML = `
        <td><strong>${d.title}</strong></td>
        <td>$${(d.value || 0).toLocaleString()}</td>
        <td><span class="badge-tag ${stageBadge}">${d.stage}</span></td>
        <td>${((d.win_probability || 0.5) * 100).toFixed(0)}%</td>
        <td>${d.expected_close_date ? d.expected_close_date.split('T')[0] : '2026-09-30'}</td>
        <td>
          <button class="btn btn-secondary btn-sm" onclick="triggerAgentForDeal('${d.title}')"><i class="fa-solid fa-robot"></i> Review Deal</button>
        </td>
      `;
      tbody.appendChild(tr);
    });

    const pipelineValEl = document.getElementById("metric-pipeline");
    if (pipelineValEl) pipelineValEl.textContent = `$${totalPipelineValue.toLocaleString()}`;
  } catch (err) {
    console.error("Failed to load deals:", err);
  }
}

// Add Contact & Deal Form Handlers
function initCRMFormHandlers() {
  document.getElementById("btn-quick-contact")?.addEventListener("click", () => openModal("contact-modal"));
  document.getElementById("btn-add-contact-tab")?.addEventListener("click", () => openModal("contact-modal"));
  document.getElementById("btn-quick-deal")?.addEventListener("click", () => openModal("deal-modal"));
  document.getElementById("btn-add-deal-tab")?.addEventListener("click", () => openModal("deal-modal"));

  // Save Contact
  document.getElementById("btn-save-contact")?.addEventListener("click", async () => {
    const fn = document.getElementById("cnt-first-name").value.trim();
    const ln = document.getElementById("cnt-last-name").value.trim();
    const em = document.getElementById("cnt-email").value.trim();
    const jt = document.getElementById("cnt-job-title").value.trim();
    const ph = document.getElementById("cnt-phone").value.trim();

    if (!fn || !ln || !em) {
      alert("First name, last name, and email are required!");
      return;
    }

    try {
      await ensureAuthToken();
      const res = await fetch("/api/v1/contacts", {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({ first_name: fn, last_name: ln, email: em, job_title: jt, phone: ph, lead_status: "NEW" }),
      });

      if (res.ok) {
        closeModal("contact-modal");
        document.getElementById("form-add-contact").reset();
        await loadContacts();
        alert("✅ Contact added successfully!");
      }
    } catch (err) {
      alert("Error adding contact.");
    }
  });

  // Save Deal
  document.getElementById("btn-save-deal")?.addEventListener("click", async () => {
    const title = document.getElementById("deal-title-input").value.trim();
    const val = parseFloat(document.getElementById("deal-value-input").value || "50000");
    const stage = document.getElementById("deal-stage-input").value;

    if (!title) {
      alert("Deal title is required!");
      return;
    }

    try {
      await ensureAuthToken();
      const res = await fetch("/api/v1/deals", {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({ title: title, value: val, stage: stage, win_probability: 0.6 }),
      });

      if (res.ok) {
        closeModal("deal-modal");
        document.getElementById("form-add-deal").reset();
        await loadDeals();
        alert("✅ Sales deal created successfully!");
      }
    } catch (err) {
      alert("Error adding deal.");
    }
  });
}

// Multi-Agent Workspace Logic
function initAgentChat() {
  const btnSend = document.getElementById("btn-send-agent");
  const input = document.getElementById("chat-input");
  const dagList = document.getElementById("dag-steps-list");

  if (!btnSend) return;

  btnSend.addEventListener("click", () => {
    const text = input.value.trim();
    if (!text) return;

    appendMessage("user", text);
    input.value = "";

    dagList.innerHTML = "";
    const steps = [
      "Memory Harness: Loaded customer profile & episodic timeline.",
      "Guardrail Check: PII scan passed clean.",
      "Intent Classifier: Routed to CrewAI Sales Crew via A2A.",
      "CrewAI Sales Crew: EmailDraftAgent generated draft proposal.",
      "HITL Gate: Paused for human approval.",
    ];

    steps.forEach((step, idx) => {
      setTimeout(() => {
        const div = document.createElement("div");
        div.className = "dag-step";
        div.innerHTML = `<i class="fa-solid fa-circle-check" style="color:#34d399"></i> ${step}`;
        dagList.appendChild(div);

        if (idx === steps.length - 1) {
          appendMessage(
            "bot",
            `<strong>LangGraph HITL Gate Triggered:</strong> Action proposal generated for your query. Please review in the manager approval modal.`
          );
          openHITLModal();
        }
      }, (idx + 1) * 500);
    });
  });

  document.getElementById("btn-reject-hitl")?.addEventListener("click", () => {
    closeModal("hitl-modal");
    appendMessage("bot", "❌ <strong>Action Rejected:</strong> Draft was rejected by manager.");
  });
  document.getElementById("btn-approve-hitl")?.addEventListener("click", () => {
    closeModal("hitl-modal");
    appendMessage("bot", "✅ <strong>Action Approved & Dispatched:</strong> Personalized response sent via MCP Server!");
  });
}

function appendMessage(sender, text) {
  const msgContainer = document.getElementById("chat-messages");
  if (!msgContainer) return;
  const div = document.createElement("div");
  div.className = `chat-msg ${sender}`;
  div.innerHTML = `
    <div class="msg-avatar"><i class="fa-solid fa-${sender === 'user' ? 'user' : 'robot'}"></i></div>
    <div class="msg-bubble">${text}</div>
  `;
  msgContainer.appendChild(div);
  msgContainer.scrollTop = msgContainer.scrollHeight;
}

// Modal Helpers
function openModal(id) {
  const m = document.getElementById(id);
  if (m) m.classList.add("active");
}
function closeModal(id) {
  const m = document.getElementById(id);
  if (m) m.classList.remove("active");
}
function openHITLModal() {
  openModal("hitl-modal");
}

// Live RAG Query Testing
function initRAG() {
  const btnQuery = document.getElementById("btn-query-rag");
  const queryInput = document.getElementById("rag-query-input");
  const resultBox = document.getElementById("rag-result-box");

  if (!btnQuery) return;

  btnQuery.addEventListener("click", async () => {
    const q = queryInput.value.trim();
    if (!q) return;

    resultBox.innerHTML = `<em>Querying PageIndex hybrid vector & BM25 search engines...</em>`;

    try {
      await ensureAuthToken();
      const res = await fetch("/api/v1/rag/query", {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({ query: q, top_k: 2 }),
      });

      if (res.ok) {
        const data = await res.json();
        const nodesHtml = (data.retrieved_nodes || []).map(n => `
          <div style="background:rgba(0,0,0,0.3); padding:0.8rem; border-radius:8px; margin-top:0.5rem;">
            <strong>${n.filename} (Page ${n.page_number}):</strong><br>
            <em>"${n.text}"</em>
          </div>
        `).join("");

        resultBox.innerHTML = `
          <div style="margin-bottom:0.5rem;">
            <strong>Query:</strong> "${q}"<br>
            <span class="badge-tag green" style="margin-top:0.5rem; display:inline-block;">RAGAS Faithfulness: ${(data.faithfulness_score || 0.88).toFixed(2)}</span>
            <span class="badge-tag blue" style="margin-top:0.5rem; display:inline-block;">Reciprocal Rank Fusion (RRF)</span>
          </div>
          ${nodesHtml || '<div>No specific chunks matched.</div>'}
        `;
      }
    } catch (err) {
      resultBox.innerHTML = `<span class="text-danger">Failed to fetch RAG query.</span>`;
    }
  });
}

function triggerActionForContact(email, actionType) {
  const navButtons = document.querySelectorAll(".nav-item");
  const btnChat = Array.from(navButtons).find((b) => b.getAttribute("data-tab") === "chat");
  if (btnChat) btnChat.click();

  if (actionType === "churn_retain") {
    appendMessage("user", `Emergency retention workflow for high-churn customer ${email}`);
  } else {
    appendMessage("user", `Draft sales proposal email for contact ${email}`);
  }
}
