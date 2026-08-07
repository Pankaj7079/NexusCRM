// NexusCRM Dashboard Logic

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initCharts();
  loadContacts();
  initAgentChat();
  initRAG();
});

// Tab Navigation
function initTabs() {
  const navButtons = document.querySelectorAll(".nav-item");
  const tabContents = document.querySelectorAll(".tab-content");
  const pageTitle = document.getElementById("page-title");

  const titles = {
    dashboard: "Executive Intelligence Dashboard",
    chat: "Multi-Agent System & Harness Workspace",
    contacts: "Contacts & Lead Intelligence",
    rag: "PageIndex Hybrid RAG Knowledge Base",
    analytics: "Predictive ML Models & Benchmarks",
  };

  navButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetTab = btn.getAttribute("data-tab");

      navButtons.forEach((b) => b.classList.remove("active"));
      tabContents.forEach((c) => c.classList.remove("active"));

      btn.classList.add("active");
      document.getElementById(`tab-${targetTab}`).classList.add("active");
      pageTitle.textContent = titles[targetTab] || "NexusCRM";
    });
  });
}

// Render Dashboard Chart.js Visualizations
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
            data: [393774, 401274, 408774, 416274, 423774, 431274],
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
        labels: ["Prospecting", "Qualification", "Needs Analysis", "Proposal", "Negotiation", "Closed Won"],
        datasets: [
          {
            label: "Deals Count",
            data: [12, 8, 6, 9, 5, 14],
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

// Load Contacts Data
async function loadContacts() {
  const tbody = document.getElementById("contacts-tbody");
  if (!tbody) return;

  try {
    const res = await fetch("/api/v1/contacts?limit=10");
    if (!res.ok) throw new Error("Auth token needed");
    const contacts = await res.json();

    tbody.innerHTML = "";
    contacts.forEach((c) => {
      const tr = document.createElement("tr");
      const scoreBadge = c.lead_score >= 80 ? "green" : c.lead_score >= 50 ? "blue" : "red";
      const churnBadge = c.churn_risk >= 0.6 ? "red" : c.churn_risk >= 0.3 ? "blue" : "green";

      tr.innerHTML = `
        <td><strong>${c.first_name} ${c.last_name}</strong></td>
        <td>${c.email}</td>
        <td>${c.job_title || "N/A"}</td>
        <td><span class="badge-tag ${scoreBadge}">${c.lead_score.toFixed(1)} / 100</span></td>
        <td><span class="badge-tag ${churnBadge}">${(c.churn_risk * 100).toFixed(0)}% Risk</span></td>
        <td><span class="badge-tag blue">${c.lead_status.toUpperCase()}</span></td>
        <td><button class="btn btn-secondary btn-sm" onclick="triggerAgentForContact('${c.email}')"><i class="fa-solid fa-paper-plane"></i> Draft Email</button></td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    // Demo Mock Data
    tbody.innerHTML = `
      <tr><td><strong>Jane Doe</strong></td><td>jane.doe@acme.com</td><td>VP of Sales</td><td><span class="badge-tag green">88.5 / 100</span></td><td><span class="badge-tag green">12% Risk</span></td><td><span class="badge-tag blue">QUALIFIED</span></td><td><button class="btn btn-secondary btn-sm" onclick="openHITLModal()"><i class="fa-solid fa-paper-plane"></i> Draft Email</button></td></tr>
      <tr><td><strong>Robert Smith</strong></td><td>r.smith@globex.com</td><td>CTO</td><td><span class="badge-tag blue">65.0 / 100</span></td><td><span class="badge-tag red">78% Risk</span></td><td><span class="badge-tag blue">CONTACTED</span></td><td><button class="btn btn-secondary btn-sm" onclick="openHITLModal()"><i class="fa-solid fa-paper-plane"></i> Draft Email</button></td></tr>
      <tr><td><strong>Michael Scott</strong></td><td>m.scott@dundermifflin.com</td><td>Regional Manager</td><td><span class="badge-tag green">92.0 / 100</span></td><td><span class="badge-tag green">08% Risk</span></td><td><span class="badge-tag blue">CUSTOMER</span></td><td><button class="btn btn-secondary btn-sm" onclick="openHITLModal()"><i class="fa-solid fa-paper-plane"></i> Draft Email</button></td></tr>
    `;
  }
}

// Multi-Agent Workspace & HITL Modal
function initAgentChat() {
  const btnSend = document.getElementById("btn-send-agent");
  const input = document.getElementById("chat-input");
  const msgContainer = document.getElementById("chat-messages");
  const dagList = document.getElementById("dag-steps-list");

  if (!btnSend) return;

  btnSend.addEventListener("click", () => {
    const text = input.value.trim();
    if (!text) return;

    // Append User Message
    appendMessage("user", text);
    input.value = "";

    // Simulate Agent DAG Workflow Progression
    dagList.innerHTML = "";
    const steps = [
      "Memory Harness: Loaded customer profile & episodic timeline.",
      "Guardrail Check: PII scan passed clean.",
      "Intent Classifier: Routed to CrewAI Sales Crew via A2A.",
      "CrewAI Sales Crew: EmailDraftAgent generated draft.",
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
            `<strong>LangGraph HITL Gate Triggered:</strong> Draft email for contract renewal has been generated by CrewAI Sales Crew. Please review in the manager approval modal.`
          );
          openHITLModal();
        }
      }, (idx + 1) * 600);
    });
  });

  // Modal Buttons
  document.getElementById("modal-close").addEventListener("click", closeHITLModal);
  document.getElementById("btn-reject-hitl").addEventListener("click", () => {
    closeHITLModal();
    appendMessage("bot", "❌ <strong>Action Rejected:</strong> Email draft was rejected by manager.");
  });
  document.getElementById("btn-approve-hitl").addEventListener("click", () => {
    closeHITLModal();
    appendMessage("bot", "✅ <strong>Action Approved & Dispatched:</strong> Personalized email sent via MCP Email Server!");
  });
}

function appendMessage(sender, text) {
  const msgContainer = document.getElementById("chat-messages");
  const div = document.createElement("div");
  div.className = `chat-msg ${sender}`;
  div.innerHTML = `
    <div class="msg-avatar"><i class="fa-solid fa-${sender === 'user' ? 'user' : 'robot'}"></i></div>
    <div class="msg-bubble">${text}</div>
  `;
  msgContainer.appendChild(div);
  msgContainer.scrollTop = msgContainer.scrollHeight;
}

function openHITLModal() {
  const modal = document.getElementById("hitl-modal");
  const txt = document.getElementById("hitl-draft-text");
  txt.value = `Subject: Enterprise Renewal & Platform Upgrade Options\n\nDear Client,\n\nFollowing up on our recent call regarding your annual contract renewal. We've included a 20% annual discount option along with our new AI Agentic Harness capabilities.\n\nBest regards,\nAlex Sales (NexusCRM Team)`;
  modal.classList.add("active");
}

function closeHITLModal() {
  document.getElementById("hitl-modal").classList.remove("active");
}

// RAG Query Testing
function initRAG() {
  const btnQuery = document.getElementById("btn-query-rag");
  const queryInput = document.getElementById("rag-query-input");
  const resultBox = document.getElementById("rag-result-box");

  if (!btnQuery) return;

  btnQuery.addEventListener("click", () => {
    const q = queryInput.value.trim();
    if (!q) return;

    resultBox.innerHTML = `
      <div style="margin-bottom:1rem;">
        <strong>Query:</strong> "${q}"<br>
        <span class="badge-tag green" style="margin-top:0.5rem; display:inline-block;">RAGAS Faithfulness: 0.88</span>
        <span class="badge-tag blue" style="margin-top:0.5rem; display:inline-block;">Reciprocal Rank Fusion (RRF) Fused</span>
      </div>
      <div style="background:rgba(0,0,0,0.3); padding:1rem; border-radius:8px;">
        <strong>Retrieved Source Passage (Enterprise_Pricing_Guide_2026.pdf - Page 1):</strong><br>
        <em>"Tier 3: Enterprise Custom ($199/user/month) - Multi-Agent A2A Collaboration, Dedicated MCP Servers, Custom ML Models, 24/7 SLA Support. Discount Policy: Annual billing grants a 20% flat discount on all tiers."</em>
      </div>
    `;
  });
}

function triggerAgentForContact(email) {
  const navButtons = document.querySelectorAll(".nav-item");
  const btnChat = Array.from(navButtons).find((b) => b.getAttribute("data-tab") === "chat");
  if (btnChat) btnChat.click();
  openHITLModal();
}
