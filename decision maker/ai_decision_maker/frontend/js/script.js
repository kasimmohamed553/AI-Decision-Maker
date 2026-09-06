// ---------- Auth guard ----------
const token = localStorage.getItem("token");
const user = JSON.parse(localStorage.getItem("user") || "null");

if (!token) {
  window.location.href = "login.html";
}

document.getElementById("userChip").textContent = user ? `${user.name} · ${user.email}` : "";

document.getElementById("logoutBtn").addEventListener("click", () => {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  window.location.href = "login.html";
});

// ---------- Upload UI ----------
const uploadZone = document.getElementById("uploadZone");
const fileInput = document.getElementById("fileInput");
const browseBtn = document.getElementById("browseBtn");
const analyzeBtn = document.getElementById("analyzeBtn");
const fileNameEl = document.getElementById("fileName");
const errorBox = document.getElementById("errorBox");
const results = document.getElementById("results");

let selectedFile = null;

browseBtn.addEventListener("click", () => fileInput.click());
uploadZone.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", () => {
  if (fileInput.files.length) setFile(fileInput.files[0]);
});

["dragenter", "dragover"].forEach(evt =>
  uploadZone.addEventListener(evt, (e) => {
    e.preventDefault();
    uploadZone.classList.add("dragover");
  })
);
["dragleave", "drop"].forEach(evt =>
  uploadZone.addEventListener(evt, (e) => {
    e.preventDefault();
    uploadZone.classList.remove("dragover");
  })
);
uploadZone.addEventListener("drop", (e) => {
  if (e.dataTransfer.files.length) setFile(e.dataTransfer.files[0]);
});

function setFile(file) {
  selectedFile = file;
  fileNameEl.textContent = file.name;
  analyzeBtn.disabled = false;
  hideError();
}

function showError(text) {
  errorBox.textContent = text;
  errorBox.classList.add("show");
}
function hideError() {
  errorBox.classList.remove("show");
}

// ---------- Analyze ----------
analyzeBtn.addEventListener("click", async () => {
  if (!selectedFile) return;

  hideError();
  results.classList.remove("show");
  analyzeBtn.disabled = true;
  analyzeBtn.innerHTML = `<span class="spinner"></span> Analyzing...`;

  const formData = new FormData();
  formData.append("file", selectedFile);

  try {
    const res = await fetch(`${API_BASE}/upload`, {
      method: "POST",
      headers: { "Authorization": `Bearer ${token}` },
      body: formData
    });

    if (res.status === 401) {
      showError("Your session expired. Please log in again.");
      localStorage.removeItem("token");
      setTimeout(() => window.location.href = "login.html", 1200);
      return;
    }

    const data = await res.json();

    if (!data.success) {
      showError(data.error || data.message || "Something went wrong while analyzing the file.");
      return;
    }

    renderResults(data);

  } catch (err) {
    showError("Could not reach the server. Make sure the Flask backend is running at " + API_BASE);
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = "Analyze & Decide";
  }
});

// ---------- Render results ----------
function renderResults(data) {
  const { summary, recommendations, decision } = data;

  if (decision.status !== "success") {
    showError(decision.message || "The decision engine could not process this data.");
    return;
  }

  results.classList.add("show");

  // Verdict + signal
  const verdictEl = document.getElementById("verdictValue");
  verdictEl.textContent = decision.verdict;
  verdictEl.className = "verdict-value " + decision.signal;

  document.getElementById("confidenceText").textContent =
    `Confidence: ${decision.confidence}%  ·  Score: ${decision.score > 0 ? "+" : ""}${decision.score}`;

  const fill = document.getElementById("confidenceFill");
  fill.style.width = decision.confidence + "%";
  fill.className = "confidence-bar-fill " + decision.signal;

  document.getElementById("recommendedAction").textContent = decision.recommended_action;

  // Meter SVG
  document.getElementById("meterSvg").innerHTML = renderMeter(decision.score, decision.signal);

  // Key stats
  const statsList = document.getElementById("statsList");
  statsList.innerHTML = "";
  const statRows = [
    ["Total Sales", `$${summary.total_sales.toLocaleString()}`],
    ["Total Orders", summary.total_orders],
    ["Avg Order Value", `$${summary.average_order_value.toLocaleString()}`],
    ["Max Order", `$${summary.max_order.toLocaleString()}`],
  ];
  if (summary.growth_rate_pct !== undefined) {
    statRows.push(["Growth Rate", `${summary.growth_rate_pct > 0 ? "+" : ""}${summary.growth_rate_pct}%`]);
  }
  if (summary.top_region) statRows.push(["Top Region", summary.top_region]);
  if (summary.top_category) statRows.push(["Top Category", summary.top_category]);

  statRows.forEach(([label, value]) => {
    const row = document.createElement("div");
    row.className = "stat-row";
    row.innerHTML = `<span>${label}</span><span>${value}</span>`;
    statsList.appendChild(row);
  });

  // Reasons
  const reasonList = document.getElementById("reasonList");
  reasonList.innerHTML = "";
  decision.reasons.forEach(r => {
    const li = document.createElement("li");
    li.textContent = r;
    reasonList.appendChild(li);
  });

  // Recommendations
  const tipList = document.getElementById("tipList");
  tipList.innerHTML = "";
  (recommendations || []).forEach(t => {
    const li = document.createElement("li");
    li.textContent = t;
    tipList.appendChild(li);
  });

  // Product breakdown
  const productList = document.getElementById("productList");
  productList.innerHTML = "";
  if (summary.product_breakdown) {
    Object.entries(summary.product_breakdown).forEach(([name, value]) => {
      const row = document.createElement("div");
      row.className = "stat-row";
      row.innerHTML = `<span>${name}</span><span>$${value.toLocaleString()}</span>`;
      productList.appendChild(row);
    });
  } else {
    productList.innerHTML = `<p style="font-size:13px;">Add a 'Product' column to see this breakdown.</p>`;
  }

  results.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ---------- Signature element: the decision meter (SVG gauge) ----------
function renderMeter(score, signal) {
  // score: -100 to 100 -> angle: -90deg (stop) to +90deg (go), 0 = maintain (top)
  const clamped = Math.max(-100, Math.min(100, score));
  const angle = (clamped / 100) * 90; // degrees, needle rotation from vertical
  const colorMap = { go: "#35D68C", caution: "#F0B94D", stop: "#EC5B5B" };
  const needleColor = colorMap[signal] || "#F0B94D";

  const cx = 90, cy = 90, r = 70;

  return `
  <svg width="180" height="110" viewBox="0 0 180 110" xmlns="http://www.w3.org/2000/svg">
    <path d="M 20 90 A 70 70 0 0 1 160 90" fill="none" stroke="#2A3242" stroke-width="14" stroke-linecap="round"/>
    <path d="M 20 90 A 70 70 0 0 1 66 25" fill="none" stroke="#EC5B5B" stroke-width="14" stroke-linecap="round" opacity="0.85"/>
    <path d="M 66 25 A 70 70 0 0 1 114 25" fill="none" stroke="#F0B94D" stroke-width="14" stroke-linecap="round" opacity="0.85"/>
    <path d="M 114 25 A 70 70 0 0 1 160 90" fill="none" stroke="#35D68C" stroke-width="14" stroke-linecap="round" opacity="0.85"/>
    <g transform="rotate(${angle} ${cx} ${cy})">
      <line x1="${cx}" y1="${cy}" x2="${cx}" y2="${cy - r + 18}" stroke="${needleColor}" stroke-width="3" stroke-linecap="round"/>
    </g>
    <circle cx="${cx}" cy="${cy}" r="7" fill="${needleColor}"/>
    <text x="20" y="105" font-family="IBM Plex Mono, monospace" font-size="9" fill="#5C6579">REDUCE</text>
    <text x="145" y="105" font-family="IBM Plex Mono, monospace" font-size="9" fill="#5C6579" text-anchor="end">EXPAND</text>
  </svg>`;
}
