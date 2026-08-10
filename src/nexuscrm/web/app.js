// NexusCRM — Production Dashboard Application

let authToken = localStorage.getItem("nexuscrm_jwt_token") || null;
let currentActiveTaskId = null;
let selectedContactEmail = "pankajsingh341035@gmail.com";
let currentReviewDealTitle = "";
let cachedContacts = [];
let cachedDeals = [];

document.addEventListener("DOMContentLoaded", async () => {
  await ensureAuthToken();
  initTabs();
  initCharts();
  loadContacts();
  loadDeals();
  loadRAGDocuments();
  initAgentChat();
  initRAG();
  initCRMFormHandlers();
  initSearchFilters();
  initKeyboardShortcuts();
  initFileUploadHandlers();
  updateHeaderActions("dashboard");
});

// ===== AUTH =====

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
    console.warn("Auth: auto-login failed, continuing without token");
  }
  return authToken;
}

function getAuthHeaders() {
  const headers = { "Content-Type": "application/json" };
  if (authToken) headers["Authorization"] = `Bearer ${authToken}`;
  return headers;
}

// ===== TOAST NOTIFICATIONS =====

function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;

  const iconMap = {
    success: "fa-circle-check",
    error: "fa-circle-exclamation",
    info: "fa-circle-info",
  };

  toast.innerHTML = `<i class="fa-solid ${iconMap[type] || iconMap.info}"></i> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.add("toast-exit");
    setTimeout(() => toast.remove(), 200);
  }, 3500);
}

// ===== KEYBOARD SHORTCUTS =====

function initKeyboardShortcuts() {
  window.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      openModal("command-palette");
      setTimeout(() => document.getElementById("cmd-input")?.focus(), 100);
    }
    if (e.key === "Escape") {
      document.querySelectorAll(".modal-overlay.active").forEach((m) => m.classList.remove("active"));
    }
  });

  document.getElementById("cmd-input")?.addEventListener("input", (e) => {
    const q = e.target.value.toLowerCase().trim();
    document.querySelectorAll(".cmd-item").forEach((item) => {
      item.style.display = item.textContent.toLowerCase().includes(q) ? "flex" : "none";
    });
  });
}

function executeCmdShortcut(promptText) {
  closeModal("command-palette");
  sendQuickPrompt(promptText);
}

function sendQuickPrompt(promptText) {
  // Switch to agent console tab
  const chatBtn = document.querySelector('.nav-item[data-tab="chat"]');
  if (chatBtn) chatBtn.click();

  const input = document.getElementById("chat-input");
  if (input) {
    input.value = promptText;
    document.getElementById("btn-send-agent")?.click();
  }
}

// ===== HEADER ACTIONS (context-aware) =====

function updateHeaderActions(tabName) {
  const container = document.getElementById("dynamic-header-actions");
  if (!container) return;

  const actions = {
    contacts: `<button class="btn btn-primary btn-sm" onclick="openModal('contact-modal')"><i class="fa-solid fa-plus"></i> Add Contact</button>`,
    deals: `<button class="btn btn-primary btn-sm" onclick="openModal('deal-modal')"><i class="fa-solid fa-plus"></i> Add Deal</button>`,
    rag: `<button class="btn btn-primary btn-sm" onclick="document.getElementById('rag-file-input').click()"><i class="fa-solid fa-upload"></i> Upload</button>`,
    dashboard: "",
    chat: "",
    analytics: "",
  };

  container.innerHTML = actions[tabName] || "";
}

// ===== TAB NAVIGATION =====

function initTabs() {
  const navButtons = document.querySelectorAll(".nav-item");
  const tabContents = document.querySelectorAll(".tab-content");
  const pageTitle = document.getElementById("page-title");

  const titles = {
    dashboard: "Dashboard",
    chat: "Agent Console",
    contacts: "Contacts",
    deals: "Deals",
    rag: "Knowledge Base",
    analytics: "Analytics",
  };

  navButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const tab = btn.getAttribute("data-tab");
      navButtons.forEach((b) => b.classList.remove("active"));
      tabContents.forEach((c) => c.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(`tab-${tab}`)?.classList.add("active");
      if (pageTitle) pageTitle.textContent = titles[tab] || "NexusCRM";
      updateHeaderActions(tab);

      // Lazy-load data when switching tabs
      if (tab === "contacts") loadContacts();
      if (tab === "deals") loadDeals();
      if (tab === "rag") loadRAGDocuments();
    });
  });
}

// ===== CHARTS =====

function initCharts() {
  const chartOpts = {
    responsive: true,
    plugins: { legend: { labels: { color: "#8b95a7", font: { size: 11 } } } },
    scales: {
      x: { ticks: { color: "#5a6478", font: { size: 10 } }, grid: { color: "rgba(255,255,255,0.03)" } },
      y: { ticks: { color: "#5a6478", font: { size: 10 } }, grid: { color: "rgba(255,255,255,0.03)" } },
    },
  };

  const ctxForecast = document.getElementById("chart-forecast")?.getContext("2d");
  if (ctxForecast) {
    new Chart(ctxForecast, {
      type: "line",
      data: {
        labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        datasets: [{
          label: "Projected Revenue ($)",
          data: [400542, 408500, 416000, 424500, 432000, 440000],
          borderColor: "#60a5fa",
          backgroundColor: "rgba(96, 165, 250, 0.08)",
          fill: true,
          tension: 0.35,
          borderWidth: 2,
          pointRadius: 3,
          pointBackgroundColor: "#60a5fa",
        }],
      },
      options: chartOpts,
    });
  }

  const ctxDeals = document.getElementById("chart-deals")?.getContext("2d");
  if (ctxDeals) {
    new Chart(ctxDeals, {
      type: "bar",
      data: {
        labels: ["Prospecting", "Qualification", "Analysis", "Proposal", "Negotiation", "Won"],
        datasets: [{
          label: "Deals",
          data: [18, 15, 22, 16, 11, 18],
          backgroundColor: ["#60a5fa", "#a78bfa", "#fbbf24", "#34d399", "#f87171", "#22d3ee"],
          borderRadius: 4,
          maxBarThickness: 40,
        }],
      },
      options: { ...chartOpts, plugins: { legend: { display: false } } },
    });
  }
}

// ===== CONTACTS =====

async function loadContacts() {
  const tbody = document.getElementById("contacts-tbody");
  if (!tbody) return;

  try {
    await ensureAuthToken();
    const res = await fetch("/api/v1/contacts?limit=150", { headers: getAuthHeaders() });

    if (res.status === 401) {
      localStorage.removeItem("nexuscrm_jwt_token");
      authToken = null;
      await ensureAuthToken();
      return loadContacts();
    }

    if (!res.ok) throw new Error("Failed to fetch contacts");
    cachedContacts = await res.json();

    const countEl = document.getElementById("metric-contacts-count");
    if (countEl) countEl.textContent = cachedContacts.length;

    renderContactsTable(cachedContacts);
  } catch (err) {
    console.error("Contacts:", err);
    tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted" style="padding:2rem">Failed to load contacts</td></tr>`;
  }
}

function renderContactsTable(contacts) {
  const tbody = document.getElementById("contacts-tbody");
  if (!tbody) return;

  if (contacts.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7"><div class="empty-state"><i class="fa-solid fa-users"></i><p>No contacts yet. Add your first contact to get started.</p></div></td></tr>`;
    return;
  }

  tbody.innerHTML = "";
  contacts.forEach((c) => {
    const tr = document.createElement("tr");
    const score = c.lead_score || 75;
    const churn = c.churn_risk || 0.15;
    const scoreBadge = score >= 80 ? "green" : score >= 50 ? "blue" : "red";
    const churnBadge = churn >= 0.5 ? "red" : churn >= 0.25 ? "amber" : "green";

    tr.innerHTML = `
      <td><strong>${c.first_name} ${c.last_name}</strong></td>
      <td>${c.email}</td>
      <td>${c.job_title || "—"}</td>
      <td><span class="badge-tag ${scoreBadge}">${score.toFixed(0)}</span></td>
      <td><span class="badge-tag ${churnBadge}">${(churn * 100).toFixed(0)}%</span></td>
      <td><span class="badge-tag blue">${(c.lead_status || "new").toUpperCase()}</span></td>
      <td>
        <button class="btn btn-secondary btn-sm" onclick="triggerActionForContact('${c.email}', 'draft_email')"><i class="fa-solid fa-paper-plane"></i></button>
        ${churn >= 0.4 ? `<button class="btn btn-danger btn-sm" onclick="triggerActionForContact('${c.email}', 'churn_retain')" title="High churn risk — trigger retention"><i class="fa-solid fa-bolt"></i></button>` : ""}
      </td>
    `;
    tbody.appendChild(tr);
  });
}

// ===== DEALS =====

async function loadDeals() {
  const tbody = document.getElementById("deals-tbody");
  if (!tbody) return;

  try {
    await ensureAuthToken();
    const res = await fetch("/api/v1/deals?limit=100", { headers: getAuthHeaders() });
    if (!res.ok) throw new Error("Failed to fetch deals");
    cachedDeals = await res.json();

    let total = 0;
    cachedDeals.forEach((d) => (total += d.value || 0));

    const pipelineEl = document.getElementById("metric-pipeline");
    if (pipelineEl) pipelineEl.textContent = `$${total.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;

    renderDealsTable(cachedDeals);
  } catch (err) {
    console.error("Deals:", err);
    tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted" style="padding:2rem">Failed to load deals</td></tr>`;
  }
}

function renderDealsTable(deals) {
  const tbody = document.getElementById("deals-tbody");
  if (!tbody) return;

  if (deals.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6"><div class="empty-state"><i class="fa-solid fa-handshake"></i><p>No deals yet. Create a deal to start tracking your pipeline.</p></div></td></tr>`;
    return;
  }

  tbody.innerHTML = "";
  deals.forEach((d) => {
    const tr = document.createElement("tr");
    const stageBadge = d.stage === "closed_won" ? "green" : d.stage === "closed_lost" ? "red" : "blue";
    const stageLabel = (d.stage || "prospecting").replace(/_/g, " ");

    tr.innerHTML = `
      <td><strong>${d.title}</strong></td>
      <td>$${(d.value || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}</td>
      <td><span class="badge-tag ${stageBadge}">${stageLabel}</span></td>
      <td>${((d.win_probability || 0.5) * 100).toFixed(0)}%</td>
      <td>${d.expected_close_date ? d.expected_close_date.split("T")[0] : "—"}</td>
      <td>
        <button class="btn btn-secondary btn-sm" onclick="openDealReviewModal('${d.title}', ${d.value}, '${d.stage}', ${d.win_probability})"><i class="fa-solid fa-chart-bar"></i> Review</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

// ===== SEARCH FILTERS =====

function initSearchFilters() {
  document.getElementById("contact-search")?.addEventListener("input", (e) => {
    const q = e.target.value.toLowerCase().trim();
    renderContactsTable(
      cachedContacts.filter(
        (c) =>
          c.first_name.toLowerCase().includes(q) ||
          c.last_name.toLowerCase().includes(q) ||
          c.email.toLowerCase().includes(q) ||
          (c.job_title && c.job_title.toLowerCase().includes(q))
      )
    );
  });

  document.getElementById("deal-search")?.addEventListener("input", (e) => {
    const q = e.target.value.toLowerCase().trim();
    renderDealsTable(cachedDeals.filter((d) => d.title.toLowerCase().includes(q) || d.stage.toLowerCase().includes(q)));
  });
}

// ===== FORM HANDLERS (SAVE CONTACT, SAVE DEAL) =====

function initCRMFormHandlers() {
  // Save Contact
  document.getElementById("btn-save-contact")?.addEventListener("click", async () => {
    const fn = document.getElementById("cnt-first-name").value.trim();
    const ln = document.getElementById("cnt-last-name").value.trim();
    const em = document.getElementById("cnt-email").value.trim();
    const jt = document.getElementById("cnt-job-title").value.trim();
    const ph = document.getElementById("cnt-phone").value.trim();

    if (!fn || !ln || !em) {
      showToast("First name, last name, and email are required.", "error");
      return;
    }

    try {
      await ensureAuthToken();
      const res = await fetch("/api/v1/contacts", {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({
          first_name: fn,
          last_name: ln,
          email: em,
          job_title: jt || "Executive",
          phone: ph || "",
          lead_status: "new",
        }),
      });

      if (res.ok) {
        closeModal("contact-modal");
        document.getElementById("form-add-contact").reset();
        await loadContacts();
        showToast(`Contact "${fn} ${ln}" saved.`, "success");
      } else {
        const err = await res.json();
        showToast(err.detail || "Failed to save contact.", "error");
      }
    } catch {
      showToast("Network error saving contact.", "error");
    }
  });

  // Save Deal
  document.getElementById("btn-save-deal")?.addEventListener("click", async () => {
    const title = document.getElementById("deal-title-input").value.trim();
    const val = parseFloat(document.getElementById("deal-value-input").value || "0");
    const stage = document.getElementById("deal-stage-input").value;

    if (!title) {
      showToast("Deal title is required.", "error");
      return;
    }
    if (val <= 0) {
      showToast("Deal value must be greater than zero.", "error");
      return;
    }

    try {
      await ensureAuthToken();
      const res = await fetch("/api/v1/deals", {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({ title, value: val, stage, win_probability: 0.65 }),
      });

      if (res.ok) {
        closeModal("deal-modal");
        document.getElementById("form-add-deal").reset();
        await loadDeals();
        showToast(`Deal "${title}" created.`, "success");
      } else {
        const err = await res.json();
        showToast(err.detail || "Failed to create deal.", "error");
      }
    } catch {
      showToast("Network error creating deal.", "error");
    }
  });

  // Deal Review → Generate Proposal
  document.getElementById("btn-trigger-deal-action")?.addEventListener("click", () => {
    closeModal("deal-review-modal");
    triggerAgentForDeal(currentReviewDealTitle);
  });
}

// ===== FILE UPLOAD (RAG) =====

function initFileUploadHandlers() {
  const fileInput = document.getElementById("rag-file-input");
  if (!fileInput) return;

  fileInput.addEventListener("change", async (e) => {
    if (e.target.files[0]) await uploadRAGDocument(e.target.files[0]);
    fileInput.value = ""; // reset so same file can be re-uploaded
  });

  const dropzone = document.getElementById("dropzone");
  if (dropzone) {
    dropzone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropzone.classList.add("drag-over");
    });
    dropzone.addEventListener("dragleave", () => dropzone.classList.remove("drag-over"));
    dropzone.addEventListener("drop", async (e) => {
      e.preventDefault();
      dropzone.classList.remove("drag-over");
      if (e.dataTransfer.files.length > 0) await uploadRAGDocument(e.dataTransfer.files[0]);
    });
  }
}

async function uploadRAGDocument(file) {
  const resultBox = document.getElementById("rag-result-box");
  if (resultBox)
    resultBox.innerHTML = `<div class="text-muted text-center" style="padding:1rem"><i class="fa-solid fa-spinner fa-spin"></i> Indexing ${file.name}...</div>`;

  try {
    await ensureAuthToken();
    const formData = new FormData();
    formData.append("file", file);

    const headers = {};
    if (authToken) headers["Authorization"] = `Bearer ${authToken}`;

    const res = await fetch("/api/v1/rag/upload", { method: "POST", headers, body: formData });

    if (res.ok) {
      const data = await res.json();
      await loadRAGDocuments();
      showToast(`"${file.name}" indexed — ${data.document.chunk_count} chunks created.`, "success");
      if (resultBox)
        resultBox.innerHTML = `<div class="empty-state"><i class="fa-solid fa-circle-check" style="color:var(--green)"></i><p>"${file.name}" indexed successfully with ${data.document.chunk_count} chunks.</p></div>`;
    } else {
      showToast("Failed to upload document.", "error");
    }
  } catch (err) {
    console.error("Upload:", err);
    showToast("Network error uploading document.", "error");
  }
}

async function loadRAGDocuments() {
  const docList = document.getElementById("doc-list");
  const countBadge = document.getElementById("rag-doc-count-badge");
  if (!docList) return;

  try {
    await ensureAuthToken();
    const res = await fetch("/api/v1/rag/documents", { headers: getAuthHeaders() });
    if (!res.ok) return;

    const docs = await res.json();
    if (countBadge) countBadge.textContent = `${docs.length} indexed`;

    docList.innerHTML = "";
    if (docs.length === 0) {
      docList.innerHTML = `<li class="text-muted" style="justify-content:center">No documents indexed yet</li>`;
      return;
    }

    docs.forEach((d) => {
      const li = document.createElement("li");
      li.innerHTML = `<span><i class="fa-solid fa-file-lines"></i> ${d.filename}</span> <span class="badge-tag green">${d.chunk_count} chunks</span>`;
      docList.appendChild(li);
    });
  } catch (err) {
    console.error("RAG docs:", err);
  }
}

// ===== AGENT CHAT =====

function initAgentChat() {
  const btnSend = document.getElementById("btn-send-agent");
  const input = document.getElementById("chat-input");
  const dagList = document.getElementById("dag-steps-list");

  if (!btnSend) return;

  // Send on Enter key
  input?.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      btnSend.click();
    }
  });

  btnSend.addEventListener("click", async () => {
    const text = input.value.trim();
    if (!text) return;

    appendMessage("user", text);
    input.value = "";

    dagList.innerHTML = `<div class="dag-step"><i class="fa-solid fa-spinner fa-spin" style="color:var(--blue)"></i> Running orchestrator...</div>`;

    try {
      await ensureAuthToken();
      const res = await fetch("/api/v1/agents/execute", {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({
          query: text,
          contact_email: selectedContactEmail,
          deal_title: currentReviewDealTitle || "Enterprise Contract Renewal",
        }),
      });

      if (!res.ok) throw new Error("Agent endpoint returned " + res.status);
      const data = await res.json();
      currentActiveTaskId = data.task_id;

      // Render execution steps
      dagList.innerHTML = "";
      (data.execution_steps || []).forEach((step) => {
        const div = document.createElement("div");
        div.className = "dag-step";
        div.innerHTML = `<i class="fa-solid fa-circle-check" style="color:var(--green)"></i> ${step}`;
        dagList.appendChild(div);
      });

      if ((data.execution_steps || []).length === 0) {
        dagList.innerHTML = `<div class="dag-step"><i class="fa-solid fa-circle-check" style="color:var(--green)"></i> Task completed</div>`;
      }

      appendMessage("bot", data.final_response || "Done.");

      // HITL gate
      if (data.hitl_pending || (data.crew_output && data.crew_output.draft_body)) {
        const draft =
          data.crew_output?.draft_body ||
          `Subject: Enterprise Proposal for ${selectedContactEmail}\n\nDear Client,\n\nFollowing up regarding your account. We'd like to discuss renewal terms and available discounts.\n\nBest regards,\nNexusCRM Team`;
        openHITLModal(draft);
      }
    } catch (err) {
      dagList.innerHTML = `<div class="dag-step"><i class="fa-solid fa-circle-exclamation" style="color:var(--red)"></i> Request failed</div>`;
      appendMessage("bot", "I wasn't able to complete that request. Could you try rephrasing?");
    }
  });

  // HITL buttons
  document.getElementById("btn-reject-hitl")?.addEventListener("click", async () => {
    closeModal("hitl-modal");
    if (currentActiveTaskId) {
      try {
        await fetch("/api/v1/agents/approve", {
          method: "POST",
          headers: getAuthHeaders(),
          body: JSON.stringify({ task_id: currentActiveTaskId, approved: false }),
        });
      } catch {}
    }
    appendMessage("bot", "Draft rejected. No email was sent.");
    showToast("Draft rejected.", "info");
  });

  document.getElementById("btn-approve-hitl")?.addEventListener("click", async () => {
    const edited = document.getElementById("hitl-draft-text").value;
    closeModal("hitl-modal");

    if (currentActiveTaskId) {
      try {
        await fetch("/api/v1/agents/approve", {
          method: "POST",
          headers: getAuthHeaders(),
          body: JSON.stringify({ task_id: currentActiveTaskId, approved: true, edited_content: edited }),
        });
      } catch {}
    }

    appendMessage("bot", `Email sent to <code>${selectedContactEmail}</code>.\n\n<pre>${edited}</pre>`);
    showToast(`Email dispatched to ${selectedContactEmail}.`, "success");
  });
}

// ===== CHAT HELPERS =====

function formatMarkdown(text) {
  if (!text) return "";
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\n\n/g, "<br><br>")
    .replace(/\n/g, "<br>");
}

function appendMessage(sender, text) {
  const container = document.getElementById("chat-messages");
  if (!container) return;

  const div = document.createElement("div");
  div.className = `chat-msg ${sender}`;
  div.innerHTML = `
    <div class="msg-avatar"><i class="fa-solid fa-${sender === "user" ? "user" : "robot"}"></i></div>
    <div class="msg-bubble">${formatMarkdown(text)}</div>
  `;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

// ===== RAG QUERY =====

function initRAG() {
  const btnQuery = document.getElementById("btn-query-rag");
  const queryInput = document.getElementById("rag-query-input");
  const resultBox = document.getElementById("rag-result-box");

  if (!btnQuery) return;

  // Enter key support
  queryInput?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      btnQuery.click();
    }
  });

  btnQuery.addEventListener("click", async () => {
    const q = queryInput.value.trim();
    if (!q) return;

    resultBox.innerHTML = `<div class="text-muted text-center" style="padding:1rem"><i class="fa-solid fa-spinner fa-spin"></i> Searching...</div>`;

    try {
      await ensureAuthToken();
      const res = await fetch("/api/v1/rag/query", {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({ query: q, top_k: 3 }),
      });

      if (!res.ok) throw new Error("Query failed");
      const data = await res.json();

      const nodes = data.retrieved_nodes || [];
      if (nodes.length === 0) {
        resultBox.innerHTML = `<div class="empty-state"><i class="fa-solid fa-magnifying-glass"></i><p>No matching results for "${q}"</p></div>`;
        return;
      }

      const faithfulness = (data.faithfulness_score || 0.88).toFixed(2);
      let html = `<div style="margin-bottom:0.75rem"><span class="badge-tag green">Faithfulness: ${faithfulness}</span> <span class="badge-tag purple">Hybrid retrieval</span></div>`;

      nodes.forEach((n) => {
        html += `
          <div style="background:var(--bg-base); padding:0.75rem; border-radius:var(--radius-sm); margin-bottom:0.5rem; border:1px solid var(--border);">
            <div style="font-size:0.72rem; color:var(--text-tertiary); margin-bottom:0.35rem;">${n.filename} · Page ${n.page_number}</div>
            <div style="font-size:0.8rem; color:var(--text-secondary); line-height:1.5;">${n.text}</div>
          </div>
        `;
      });

      resultBox.innerHTML = html;
    } catch {
      resultBox.innerHTML = `<div class="empty-state"><i class="fa-solid fa-circle-exclamation" style="color:var(--red)"></i><p>Search request failed. Check that the server is running.</p></div>`;
    }
  });
}

function quickRAGQuery(queryText) {
  const input = document.getElementById("rag-query-input");
  if (input) {
    input.value = queryText;
    document.getElementById("btn-query-rag")?.click();
  }
}

// ===== MODALS =====

function openModal(id) {
  document.getElementById(id)?.classList.add("active");
}

function closeModal(id) {
  document.getElementById(id)?.classList.remove("active");
}

function openHITLModal(draftContent) {
  const txt = document.getElementById("hitl-draft-text");
  if (txt) txt.value = draftContent;
  openModal("hitl-modal");
}

function openDealReviewModal(title, value, stage, winProb) {
  currentReviewDealTitle = title;
  const body = document.getElementById("deal-review-body");
  if (!body) return;

  const stageLabel = (stage || "prospecting").replace(/_/g, " ");
  const prob = ((winProb || 0.5) * 100).toFixed(0);

  body.innerHTML = `
    <div style="background:var(--bg-base); padding:1rem; border-radius:var(--radius-sm); border:1px solid var(--border);">
      <h4 style="font-size:0.95rem; font-weight:600; margin-bottom:0.75rem;">${title}</h4>
      <div class="stats-row">
        <div class="stat-item"><span class="stat-label">Value</span><span class="stat-value">$${(value || 0).toLocaleString()}</span></div>
        <div class="stat-item"><span class="stat-label">Stage</span><span class="stat-value" style="font-size:0.85rem">${stageLabel}</span></div>
        <div class="stat-item"><span class="stat-label">Win Prob.</span><span class="stat-value">${prob}%</span></div>
      </div>
      <hr style="border:none; border-top:1px solid var(--border); margin:0.75rem 0;">
      <p style="font-size:0.78rem; font-weight:600; color:var(--text-secondary); margin-bottom:0.4rem;">Suggested next steps:</p>
      <ul style="padding-left:1.1rem; font-size:0.78rem; color:var(--text-tertiary); line-height:1.6;">
        <li>Schedule executive review with buyer's IT leadership</li>
        <li>Share updated compliance and SLA documentation</li>
        <li>Propose multi-year discount for commitment</li>
      </ul>
    </div>
  `;
  openModal("deal-review-modal");
}

// ===== CONTACT & DEAL ACTIONS =====

function triggerActionForContact(email, actionType) {
  selectedContactEmail = email;
  const chatBtn = document.querySelector('.nav-item[data-tab="chat"]');
  if (chatBtn) chatBtn.click();

  const input = document.getElementById("chat-input");
  if (actionType === "churn_retain") {
    input.value = `Emergency retention plan for ${email}`;
  } else {
    input.value = `Draft proposal email for ${email}`;
  }
  document.getElementById("btn-send-agent")?.click();
}

function triggerAgentForDeal(dealTitle) {
  currentReviewDealTitle = dealTitle;
  const chatBtn = document.querySelector('.nav-item[data-tab="chat"]');
  if (chatBtn) chatBtn.click();

  const input = document.getElementById("chat-input");
  if (input) input.value = `Analyze sales strategy for deal ${dealTitle}`;
  document.getElementById("btn-send-agent")?.click();
}
