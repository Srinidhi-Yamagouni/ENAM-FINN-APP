"use strict";
const $ = (s, r = document) => r.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const api = (u, o) => fetch(u, o).then(async r => { if (!r.ok) { let m = r.status; try { m = (await r.json()).detail || m } catch { } throw new Error(m); } return r.json(); });
const ls = { get: (k, d) => { try { return JSON.parse(localStorage.getItem("finn-v2:" + k)) ?? d } catch { return d } }, set: (k, v) => { try { localStorage.setItem("finn-v2:" + k, JSON.stringify(v)) } catch { } } };

const S = {
  note: "",
  manual: false,
  tab: "today",
  meta: null,
  hours: ls.get("hours", 24),
  volx: ls.get("volx", 2),
  px: ls.get("px", 4),
  cats: ls.get("cats", []),
  thread: [],
  netTicker: null,
  theme: null,
  mode: ls.get("mode_v2", "light")
};

const ini = n => n.split(/\s+/).map(w => w[0]).slice(0, 2).join("");
const pct = (v, d = 1) => v == null ? "–" : `<span class="${v >= 0 ? "up" : "dn"}">${v >= 0 ? "+" : ""}${v.toFixed(d)}%</span>`;
const ago = iso => { const h = (Date.now() - new Date(iso)) / 36e5; return h < 1 ? "just now" : h < 24 ? Math.round(h) + "h ago" : Math.round(h / 24) + "d ago"; };
const num = v => Number(v).toLocaleString("en-IN", { maximumFractionDigits: 1 });

function strengthDots(s = 3) {
  let dots = "";
  for (let i = 1; i <= 5; i++) {
    dots += `<span class="sdot ${i <= s ? "filled" : ""}"></span>`;
  }
  return `<span class="strength-meter" title="Relationship strength: ${s}/5">${dots}</span>`;
}

function spark(vals, w = 140, h = 32, color = "var(--ac)") {
  if (!vals || vals.length < 2) return "";
  const mn = Math.min(...vals), mx = Math.max(...vals), r = mx - mn || 1;
  const pts = vals.map((v, i) => `${(i / (vals.length - 1) * w).toFixed(1)},${(h - 4 - (v - mn) / r * (h - 8)).toFixed(1)}`).join(" ");
  return `<svg class="spark" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">
    <polyline points="${pts}" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>`;
}

function bars(vals, labels, w = 300, h = 65, fmt = num) {
  const mx = Math.max(...vals.map(Math.abs)) || 1, bw = w / vals.length;
  return `<svg width="100%" viewBox="0 0 ${w} ${h + 18}">${vals.map((v, i) => {
    const bh = Math.max(3, Math.abs(v) / mx * h);
    return `<rect x="${i * bw + 5}" y="${h - bh}" width="${bw - 10}" height="${bh}" rx="4" fill="${v < 0 ? "var(--dn)" : "var(--ac)"}" opacity=".9"/>
    <text x="${i * bw + bw / 2}" y="${h + 14}" font-size="9" font-weight="600" text-anchor="middle" fill="var(--mu)">${labels[i]}</text>
    <text x="${i * bw + bw / 2}" y="${Math.max(10, h - bh - 4)}" font-size="9" font-weight="700" text-anchor="middle" fill="var(--tx)">${fmt(v)}</text>`;
  }).join("")}</svg>`;
}

/* ---------- sheet ---------- */
function openSheet(html) {
  $("#sheetbody").innerHTML = html;
  $("#sheet").hidden = false;
  $("#scrim").hidden = false;
  $("#sheet").scrollTop = 0;
}
function closeSheet() {
  $("#sheet").hidden = true;
  $("#scrim").hidden = true;
}
$("#scrim").onclick = closeSheet;

/* ---------- shared blocks ---------- */
function contactRow(c, extra = "") {
  const p = c.contact || c;
  return `<div class="link" data-act="person" data-id="${p.id}">
    <div class="av">${esc(ini(p.name))}</div>
    <div class="link-info">
      <div class="link-name-row">
        <b>${esc(p.name)}</b>
        ${p.strength ? strengthDots(p.strength) : ""}
      </div>
      <span class="sub">${esc(p.role)}, ${esc(p.org)}</span>
      ${extra ? `<div class="link-extra">${extra}</div>` : ""}
    </div>
    <span class="link-chevron">&rsaquo;</span>
  </div>`;
}

function networkBlock(n) {
  if (!n) return "";
  let h = "";
  if (n.overlaps && n.overlaps.length) {
    h += `<div class="network-context-box">
      <div class="network-badge">OVERLAP IN YOUR NETWORK</div>
      ${n.overlaps.map(o => contactRow(o.contact, esc(o.evidence.join(" · ")) + ` <span class="sub">(last contacted ${o.contact.last_contacted_days}d ago)</span>`)).join("")}
    </div>`;
  } else if (n.overlaps) {
    h += `<div class="sub network-empty">No direct overlap identified in your immediate network.</div>`;
  }
  if (n.second_degree && n.second_degree.length) {
    h += `<div class="network-context-box secondary">
      <div class="network-badge">1 CONNECTION AWAY</div>
      ${n.second_degree.map(s => contactRow(s.via, esc(s.path))).join("")}
    </div>`;
  }
  if (n.who_to_call && n.who_to_call.length) {
    h += `<div class="network-context-box who-box">
      <div class="network-badge">BEST PERSON TO CALL</div>
      ${n.who_to_call.map(p => contactRow(p, esc(p.why))).join("")}
    </div>`;
  }
  return h;
}

function resultsBlock(r) {
  const row = (k, l) => r[k] ? `<div>${l}</div><div class="r font-bold">${num(r[k].cur)}</div><div class="r">${pct(r[k].qoq)}</div><div class="r">${pct(r[k].yoy)}</div>` : "";
  return `<div class="results-table-wrap">
    <div class="metrics">
      <div class="h">₹ cr</div><div class="h r">Quarter</div><div class="h r">QoQ</div><div class="h r">YoY</div>
      ${row("revenue", "Revenue")}
      ${row("ebitda", "EBITDA")}
      ${row("pbt", "PBT")}
      ${row("pat", "PAT")}
    </div>
    ${r.ebitda?.margin ? `<div class="margin-badge">EBITDA margin <strong>${r.ebitda.margin}%</strong> (${r.ebitda.margin_yoy_bps >= 0 ? "+" : ""}${r.ebitda.margin_yoy_bps} bps YoY)</div>` : ""}
  </div>`;
}

function filingCard(i) {
  const p = i.person;
  const net = i.network || i.relationship_graph;
  return `<div class="card ${i.tier}" data-id="${i.id}">
    <div class="top">
      <span class="tk">${i.ticker}</span>
      <span class="cat">${esc(i.label)}</span>
      <span class="sp"></span>
      <span class="time-badge">${ago(i.ts)}</span>
    </div>
    <div class="subject">${esc(i.subject)}</div>
    ${i.results ? resultsBlock(i.results) : ""}
    ${p ? `<div class="person">
      <div class="nm">${esc(p.name)} · <span class="role">${esc(p.role)}</span></div>
      <div class="person-history">${p.history.slice().reverse().map(h => `<span>${esc(h.role)}, ${esc(h.org)} <small>(${h.start}–${h.end || "now"})</small></span>`).join(" · ")}</div>
      <div class="sub person-edu">${p.edu.map(e => esc(e.school) + " '" + String(e.year).slice(-2)).join(" · ")}</div>
    </div>` : ""}
    ${i.why ? `<div class="why">${esc(i.why)}</div>` : ""}
    ${networkBlock(net)}
    <div class="card-actions">
      ${["results", "m&a", "capex"].includes(i.category) || store.ready(i.ticker) ?
        `<button class="btn btn-action primary" data-act="research" data-t="${i.ticker}"><svg class="btn-icon" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>Dig in</button>` : ""}
      <button class="btn btn-action" data-act="ask" data-q="who should I call about ${esc(i.company)}"><svg class="btn-icon" viewBox="0 0 24 24"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>Who to call</button>
    </div>
  </div>`;
}

const store = { ready: t => S.meta && S.meta.research_ready.includes(t) };

/* ---------- TODAY ---------- */
async function today() {
  $("main").classList.remove("ask-mode");
  const v = $("#view");
  v.innerHTML = `
    <div class="filter-bar">
      ${[[24, "24h"], [72, "3 days"], [168, "7 days"], [720, "30 days"]].map(([h, l]) => `<button class="chip ${S.hours == h ? "on" : ""}" data-act="hours" data-h="${h}">${l}</button>`).join("")}
    </div>
    ${S.note ? `<div class="note-banner">${esc(S.note)}</div>` : ""}
    <div id="tbody" class="loading-state"><div class="spinner"></div><span>Filtering intelligence feed...</span></div>`;

  const dashboard = await api(`/api/dashboard?hours=${S.hours}&vol_x=${S.volx}&px=${S.px}${S.cats.length ? "&cats=" + S.cats.join(",") : ""}`);
  const d = dashboard.digest, al = dashboard.alerts;

  if (!d.items.length && S.hours < 720 && !S.manual) {
    const next = S.hours < 168 ? 168 : 720;
    const lbl = h => h === 24 ? "24 hours" : h === 72 ? "3 days" : "7 days";
    S.note = `Nothing was filed in the last ${lbl(S.hours)}, so showing the last ${next === 168 ? "7 days" : "30 days"}.`;
    S.hours = next;
    return today();
  }

  const c = d.counts, must = d.items.filter(i => i.tier === "must"), look = d.items.filter(i => i.tier === "look"), rt = d.items.filter(i => i.tier === "routine");

  $("#tbody").className = "";
  $("#tbody").innerHTML = `
    <div class="summary-hero">
      <div class="summary-stat must"><span class="num">${c.must}</span><span class="label">Needs you</span></div>
      <div class="summary-stat look"><span class="num">${c.look}</span><span class="label">Worth a look</span></div>
      <div class="summary-stat routine"><span class="num">${c.routine}</span><span class="label">Routine</span></div>
    </div>

    ${al.length ? `
      <h2><span>Unusual moves</span><span class="sec-sub">Vol &ge; ${S.volx}&times; or &plusmn;${S.px}%</span></h2>
      <div class="strip">
        ${al.map(a => `
          <div class="alert">
            <div class="alert-top">
              <span class="t">${a.ticker}</span>
              ${pct(a.change)}
            </div>
            ${spark(a.spark, 150, 32, a.change >= 0 ? "var(--up)" : "var(--dn)")}
            <div class="n">${esc(a.reasons.join(" · "))}</div>
          </div>`).join("")}
      </div>` : ""}

    ${must.length ? `<h2>Needs you</h2>${must.map(filingCard).join("")}` : ""}
    ${look.length ? `<h2>Worth a look</h2>${look.map(filingCard).join("")}` : ""}

    ${d.reconnect && d.reconnect.length ? `
      <h2>Keep the network warm</h2>
      <div class="reconnect-group">
        ${d.reconnect.map(r => `
          <div class="reconnect">
            <div class="reconnect-icon">&#9889;</div>
            <div class="reconnect-body">
              <div class="reconnect-title">${esc(r.nudge)}</div>
              <div class="sub">${esc(r.event)}</div>
              <button class="btn btn-sm" data-act="person" data-id="${r.contact.id}">Open profile</button>
            </div>
          </div>`).join("")}
      </div>` : ""}

    ${rt.length ? `
      <details class="routine-details">
        <summary>${rt.length} routine compliance filings (archived)</summary>
        ${rt.map(i => `<div class="routine"><b>${i.ticker}</b> <span class="cat">${esc(i.label)}</span> <span>${esc(i.subject)}</span> <span class="sub">${ago(i.ts)}</span></div>`).join("")}
      </details>` : ""}`;
}

/* ---------- research sheet ---------- */
async function research(t, pre) {
  openSheet(`<div class="sheet-loading"><div class="spinner"></div><span>Extracting primary disclosures for ${t}…</span></div>`);
  let r;
  try {
    r = pre || await api("/api/research/" + t);
  } catch (e) {
    return openSheet(`<h3>${t}</h3><p class="sub">${esc(e.message)}</p>`);
  }
  openSheet(researchHTML(r));
}

function researchHTML(r) {
  const s = r.snapshot, t = r.trajectory, b = r.balance_sheet, c = r.cash_quality;
  const sec = (title, body, open) => `<details ${open ? "open" : ""} class="sheet-section"><summary><span class="sec-title">${title}</span></summary><div class="sec-content">${body}</div></details>`;
  return `
    <div class="sheet-header">
      <div class="sub tag-primary">${esc(r.source)} · primary sources only</div>
      <h3 class="sheet-title">${esc(r.name)}</h3>
      <p class="sheet-verdict">${esc(r.verdict)}</p>
    </div>

    <div class="kv">
      <div><b>₹${num(s.revenue_fy)} cr</b><span>FY revenue</span></div>
      <div><b>${s.ebitda_margin_fy}%</b><span>EBITDA margin</span></div>
      <div><b>${s.roe}%</b><span>ROE</span></div>
    </div>

    ${sec("Narrative vs Numbers", `
      <div class="sub mb-2">Management guidance across last 4 calls vs. reported delivery · <strong>${r.scorecard.kept}/${r.scorecard.measured}</strong> met or beaten</div>
      <table class="tbl">
        <tr><th>Call</th><th>Guidance</th><th>Delivered</th><th>Status</th></tr>
        ${r.narrative_vs_numbers.map(g => `
          <tr>
            <td><strong>${g.said_in}</strong><br><span class="sub">${g.metric === "capex" ? "capex" : g.metric === "revenue" ? "rev growth" : "EBITDA mgn"}</span></td>
            <td>${g.metric === "capex" ? "₹" + num(g.low) + " cr" : g.low === g.high ? "~" + g.low + "%" : g.low + "–" + g.high + "%"}</td>
            <td>${g.delivered == null ? "–" : g.delivered + "%"}</td>
            <td><span class="pill ${g.status}">${g.status}</span></td>
          </tr>
          ${g.note ? `<tr><td colspan="4" class="sub text-left">${esc(g.note)}</td></tr>` : ""}`).join("")}
      </table>`, true)}

    ${sec("Bull vs Bear", `
      <div class="bb">
        <div class="bu">
          <div class="bb-tag up">Bull Case</div>
          ${r.bull.length ? r.bull.map(x => `<p>${esc(x.point)}<br><small>${esc(x.source)}</small></p>`).join("") : "<p class='sub'>No standout strengths in disclosures.</p>"}
        </div>
        <div class="be">
          <div class="bb-tag dn">Bear Case</div>
          ${r.bear.length ? r.bear.map(x => `<p>${esc(x.point)}<br><small>${esc(x.source)}</small></p>`).join("") : "<p class='sub'>No major red flags identified.</p>"}
        </div>
      </div>`, true)}

    ${sec("Business Breakdown", `
      <p class="mb-2">${esc(r.business.summary)}</p>
      ${r.business.segments.map(g => `
        <div class="seg-row">
          <span class="sub seg-name">${esc(g.name)}</span>
          <div class="seg-track"><div class="seg-fill" style="width:${g.pct}%"></div></div>
          <span class="sub seg-pct">${g.pct}%</span>
        </div>`).join("")}`)}

    ${sec("Financial Trajectory", `
      <div class="sub mb-1">Revenue ₹ cr (CAGR ${t.revenue_cagr}%) · PAT CAGR ${t.pat_cagr}%</div>
      ${bars(t.revenue, t.years)}
      <div class="sub mt-3 mb-1">EBITDA Margin Trend %</div>
      ${bars(t.margin, t.years, 300, 48, v => v + "%")}`)}

    ${sec("Balance Sheet & Debt", `
      <table class="tbl">
        <tr><th></th>${b.years.map(y => `<th>${y}</th>`).join("")}</tr>
        <tr><td>Debt ₹ cr</td>${b.debt.map(x => `<td>${num(x)}</td>`).join("")}</tr>
        <tr><td>D/E</td>${b.de.map(x => `<td>${x}</td>`).join("")}</tr>
        <tr><td>WC days</td>${b.wc_days.map(x => `<td>${x}</td>`).join("")}</tr>
      </table>`)}

    ${sec("Cash Flow Quality", `
      <div class="sub mb-2">Cumulative CFO / PAT: <strong>${c.cum_cfo_to_pat}&times;</strong> · FCF ₹${num(c.cum_fcf)} cr</div>
      <table class="tbl">
        <tr><th></th>${c.years.map(y => `<th>${y}</th>`).join("")}</tr>
        <tr><td>CFO</td>${c.cfo.map(x => `<td>${num(x)}</td>`).join("")}</tr>
        <tr><td>Capex</td>${c.capex.map(x => `<td>${num(x)}</td>`).join("")}</tr>
        <tr><td>CFO/PAT</td>${c.cfo_to_pat.map(x => `<td>${x}</td>`).join("")}</tr>
      </table>`)}

    ${r.network && r.network.length ? `
      <h2>Network Intelligence for ${esc(r.name)}</h2>
      ${r.network.map(p => contactRow(p, esc(p.why))).join("")}` : ""}`;
}

/* ---------- person sheet ---------- */
async function personSheet(id) {
  const d = await api("/api/network/person/" + id), p = d.person;
  openSheet(`
    <div class="person-sheet-hero">
      <div class="av av-lg">${esc(ini(p.name))}</div>
      <div>
        <h3 class="sheet-title">${esc(p.name)}</h3>
        <div class="sub">${esc(p.role)}, <strong>${esc(p.org)}</strong></div>
        ${p.strength ? strengthDots(p.strength) : ""}
      </div>
    </div>
    ${p.met ? `<div class="person-met-note">&#128204; ${esc(p.met)} · Last spoke ${p.last}d ago</div>` : ""}

    <h2>Career Track</h2>
    <div class="timeline">
      ${p.history.slice().reverse().map(h => `
        <div class="timeline-item">
          <div class="timeline-dot"></div>
          <div><b>${esc(h.org)}</b> <span class="sub">${esc(h.role)} · ${h.start}–${h.end || "Present"}</span></div>
        </div>`).join("")}
    </div>
    <div class="sub mt-2">&#127891; ${p.edu.map(e => esc(e.school) + " (" + e.year + ")").join(" · ")}</div>

    ${p.themes && p.themes.length ? `
      <h2>Core Expertise</h2>
      <div class="row wrap">${p.themes.map(t => `<span class="chip">${esc(t)}</span>`).join("")}</div>` : ""}

    ${(d.overlaps && d.overlaps.length) || (d.second_degree && d.second_degree.length) ? `
      <h2>Connection Paths</h2>
      ${networkBlock({ overlaps: d.overlaps ? d.overlaps.slice(0, 3) : [], second_degree: d.second_degree })}` : ""}

    ${d.questions && d.questions.length ? `
      <h2>Questions Worth Asking</h2>
      <div class="questions-list">${d.questions.map(q => `<div class="q-card">&bull; ${esc(q)}</div>`).join("")}</div>` : ""}`);
}

/* ---------- ASK / COPILOT ---------- */
const SUGG = [
  "What changed today?",
  "Who should I call about Bharat Forge?",
  "What is our exposure to renewables?",
  "Any unusual volume spikes today?",
  "What did management guide for Suzlon?",
  "Who is Vikram Sethi?",
  "Who should I call about Suzlon?",
  "My go-to people on renewables",
  "Who should I reconnect with?",
  "Diligence on Maya Iyer",
  "Who competes with Bharat Forge?",
  "Who should I call about UltraTech Cement?"
];

function askView() {
  $("main").classList.add("ask-mode");
  $("#view").innerHTML = `
    <div class="thread" id="thread">
      ${S.thread.length ? S.thread.map(m => m.html).join("") : `
        <div class="ask-hero">
          <div class="ask-icon">&#10024;</div>
          <h3>FINN Investment Copilot</h3>
          <p class="sub">Ask anything about your 17 portfolio companies, filings, or who in your network can give you edge.</p>
        </div>
        <div class="sugg-container">
          <div class="sugg-label">SUGGESTED QUERIES</div>
          <div class="row wrap">
            ${SUGG.map(q => `<button class="chip chip-sugg" data-act="ask" data-q="${esc(q)}">${esc(q)}</button>`).join("")}
          </div>
        </div>`}
    </div>
    <div class="askbar">
      <div class="askbar-inner">
        <input id="q" placeholder="Ask about companies, people, or filings..." enterkeyhint="send" autocomplete="off">
        <button class="go" id="go" aria-label="Send query">
          <svg class="icon" viewBox="0 0 24 24"><path d="m5 12 14-7-3 14-4-5-7-2Z"/><path d="m12 14 7-9"/></svg>
        </button>
      </div>
    </div>`;

  const send = () => { const i = $("#q"); if (i && i.value.trim()) doAsk(i.value.trim()); };
  $("#go").onclick = send;
  $("#q").onkeydown = e => { if (e.key === "Enter") send(); };
  const m = $("#view");
  m.scrollTop = m.scrollHeight;
}

async function doAsk(q) {
  if (S.tab !== "ask") setTab("ask");
  S.thread.push({ html: `<div class="q">${esc(q)}</div>` });
  const thinkingId = `thinking-${Date.now()}`;
  S.thread.push({ id: thinkingId, html: `<div class="thinking"><div class="spinner-sm"></div><span>FINN intelligence synthesizing answer...</span></div>` });
  askView();

  try {
    const r = await api("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ q })
    });
    S.thread = S.thread.filter(m => m.id !== thinkingId);
    S.thread.push({ html: `<div class="answer-wrapper"><h2>${esc(r.title)}</h2>${renderCard(r)}</div>` });
  } catch (e) {
    S.thread = S.thread.filter(m => m.id !== thinkingId);
    S.thread.push({ html: `<div class="card answer-error"><div class="error-msg">${esc(e.message)}</div></div>` });
  }
  askView();
}

function mdInline(text) {
  let out = esc(text);
  out = out.replace(/`([^`]+)`/g, "<code>$1</code>");
  out = out.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  out = out.replace(/__([^_]+)__/g, "<strong>$1</strong>");
  out = out.replace(/(^|[^*])\*([^*]+)\*(?!\*)/g, "$1<em>$2</em>");
  out = out.replace(/(^|[^_])_([^_]+)_(?!_)/g, "$1<em>$2</em>");
  return out;
}

function markdown(text) {
  const lines = String(text ?? "").replace(/\r/g, "").split("\n"), out = [];
  let paragraph = [], list = null;
  const close = () => {
    if (paragraph.length) { out.push(`<p>${paragraph.map(mdInline).join("<br>")}</p>`); paragraph = []; }
    if (list) { out.push(`</${list}>`); list = null; }
  };
  for (const line of lines) {
    const heading = line.match(/^#{1,3}\s+(.+)$/);
    const bullet = line.match(/^\s*[-*]\s+(.+)$/);
    const numbered = line.match(/^\s*\d+[.)]\s+(.+)$/);
    if (!line.trim()) { close(); continue; }
    if (heading) { close(); out.push(`<h3>${mdInline(heading[1])}</h3>`); continue; }
    if (bullet || numbered) {
      const type = bullet ? "ul" : "ol";
      if (list !== type) { close(); out.push(`<${type}>`); list = type; }
      out.push(`<li>${mdInline((bullet || numbered)[1])}</li>`);
      continue;
    }
    if (list) close();
    paragraph.push(line);
  }
  close();
  return out.join("");
}

function renderCard(r) {
  const d = r.data;
  if (r.card === "text") return `<div class="card answer">${markdown(d.text)}</div>`;
  if (r.card === "people") return d.people.length ? `<div class="people-results">${d.people.map(p => contactRow(p, esc(p.why))).join("")}</div>` : `<div class="sub">Nobody in your network matches this query.</div>`;
  if (r.card === "warm") return `<div class="reconnect-group">${d.items.map(w => `<div class="reconnect"><div class="reconnect-icon">&#9889;</div><div class="reconnect-body"><b>${esc(w.nudge)}</b><div class="sub">${esc(w.event)}</div></div></div>`).join("")}</div>`;
  if (r.card === "digest") return `<div class="summary-hero"><div class="summary-stat must"><span class="num">${d.counts.must}</span><span class="label">Needs you</span></div><div class="summary-stat look"><span class="num">${d.counts.look}</span><span class="label">Worth a look</span></div></div>` + d.items.slice(0, 4).map(filingCard).join("") + `<button class="btn btn-block mt-2" data-act="tab" data-t="today">Open Full Overview</button>`;
  if (r.card === "person") {
    const p = d.person;
    return `<div class="card person-card-rich">
      <div class="person-sheet-hero">
        <div class="av av-lg">${esc(ini(p.name))}</div>
        <div><h3>${esc(p.name)}</h3><div class="sub">${esc(p.role)}, <strong>${esc(p.org)}</strong></div></div>
      </div>
      <div class="timeline mt-2">
        ${p.history.slice().reverse().map(h => `<div class="timeline-item"><div class="timeline-dot"></div><div>${esc(h.role)}, ${esc(h.org)} <small>(${h.start}–${h.end || "now"})</small></div></div>`).join("")}
      </div>
      ${networkBlock({ overlaps: d.overlaps ? d.overlaps.slice(0, 3) : [], second_degree: d.second_degree })}
      ${d.questions && d.questions.length ? `<div class="why mt-2">${d.questions.map(esc).join("<br>")}</div>` : ""}
    </div>`;
  }
  if (r.card === "research") {
    return `<div class="card">
      <h3 class="mb-1">${esc(d.name)}</h3>
      <p class="sheet-verdict mb-2">${esc(d.verdict)}</p>
      <div class="sub mb-2">Scorecard: <strong>${d.scorecard.kept}/${d.scorecard.measured}</strong> guidance calls delivered</div>
      <button class="btn primary" data-act="open-research" data-t="${d.ticker}">Open Primary Source Research</button>
    </div>`;
  }
  return "";
}

/* ---------- NETWORK ---------- */
async function networkView() {
  $("main").classList.remove("ask-mode");
  const m = S.meta;
  S.netTicker = S.netTicker || m.portfolio[0].ticker;
  $("#view").innerHTML = `
    <div class="network-intro">
      <div class="eyebrow">RELATIONSHIP GRAPH</div>
      <h1>Who makes the picture clearer.</h1>
      <p class="sub">Select any portfolio company. FINN surfaces contacts ranked by proximity to management, supply chains, and competitors.</p>
    </div>

    <div class="network-picker">
      <label for="nsel">Focus Company</label>
      <div class="select-wrap">
        <select id="nsel">${m.portfolio.map(c => `<option value="${c.ticker}" ${c.ticker === S.netTicker ? "selected" : ""}>${esc(c.name)} (${c.ticker})</option>`).join("")}</select>
      </div>
    </div>

    <div id="graph" class="mt-2"></div>

    <h2>Find By Industry Theme</h2>
    <div class="row wrap mb-3">${m.themes.map(t => `<button class="chip ${S.theme === t ? "on" : ""}" data-act="theme" data-t="${esc(t)}">${esc(t)}</button>`).join("")}</div>
    <div id="exp"></div>

    <h2>Full Network Directory (${m.portfolio.length} Coverage Sectors)</h2>
    <div id="directory" class="people-directory"><div class="sub">Loading relationship directory...</div></div>`;

  $("#nsel").onchange = e => { S.netTicker = e.target.value; drawGraph(); };
  drawGraph();
  drawDirectory();
  if (S.theme) drawExp();
}

async function drawGraph() {
  const g = await api("/api/network/graph/" + S.netTicker);
  $("#graph").innerHTML = `
    <div class="network-heading">
      <span>TOP INTELLIGENCE ROUTES</span>
      <b>${g.nodes.length} relevant contacts</b>
    </div>
    <div class="routes-list">
      ${g.nodes.slice(0, 5).map((p, i) => `
        <div class="network-contact" data-act="person" data-id="${p.id}">
          <div class="rank">0${i + 1}</div>
          <div class="av">${esc(ini(p.name))}</div>
          <div class="network-copy">
            <div class="network-name-row">
              <b>${esc(p.name)}</b>
              ${strengthDots(p.strength)}
            </div>
            <span>${esc(p.role)} · ${esc(p.org)}</span>
            <small>${esc(p.why || "Direct domain relevance to this sector.")}</small>
          </div>
          <div class="arrow">&rsaquo;</div>
        </div>`).join("")}
    </div>`;
}

async function drawDirectory() {
  const people = await api("/api/network/people");
  $("#directory").innerHTML = people.map(p => `
    <div class="directory-row" data-act="person" data-id="${p.id}">
      <div class="av">${esc(ini(p.name))}</div>
      <div class="network-copy">
        <div class="network-name-row">
          <b>${esc(p.name)}</b>
          ${strengthDots(p.strength)}
        </div>
        <span>${esc(p.role)} · ${esc(p.org)}</span>
        <small class="contact-time">Spoke ${p.last_contacted_days}d ago</small>
      </div>
      <div class="arrow">&rsaquo;</div>
    </div>`).join("");
}

async function drawExp() {
  const r = await api("/api/network/expertise?theme=" + encodeURIComponent(S.theme));
  $("#exp").innerHTML = r.length ? `<div class="expertise-box">${r.map(p => contactRow(p, esc(p.why))).join("")}</div>` : `<div class="sub">No direct contact matches found for ${esc(S.theme)}.</div>`;
}

/* ---------- SETTINGS ---------- */
function settings() {
  const cats = S.meta.categories.filter(c => c !== "unclassified");
  openSheet(`
    <h3 class="sheet-title">Alert Thresholds</h3>
    <label class="set">Trigger volume alerts above <b id="vx">${S.volx}</b>&times; 20-day average</label>
    <input type="range" id="volx" min="1.2" max="5" step="0.1" value="${S.volx}">

    <label class="set">Trigger price alerts beyond &plusmn;<b id="pxv">${S.px}</b>% in a day</label>
    <input type="range" id="px" min="1" max="10" step="0.5" value="${S.px}">

    <label class="set">Announcement Categories to Surface (Must-see always shown)</label>
    <div class="row wrap mt-1">${cats.map(c => `<button class="chip ${S.cats.includes(c) ? "on" : ""}" data-act="cat" data-c="${c}">${esc(S.meta.labels[c] || c)}</button>`).join("")}</div>

    <p class="sub mt-3">Preferences are stored locally on this terminal. The server remains stateless.</p>
    <button class="btn primary btn-block mt-2" id="done">Save Settings</button>`);

  $("#volx").oninput = e => { S.volx = +e.target.value; $("#vx").textContent = S.volx; };
  $("#px").oninput = e => { S.px = +e.target.value; $("#pxv").textContent = S.px; };
  $("#done").onclick = () => { ls.set("volx", S.volx); ls.set("px", S.px); ls.set("cats", S.cats); closeSheet(); render(); };
}

/* ---------- WIRING ---------- */
function setTab(t) {
  S.tab = t;
  document.querySelectorAll("nav button").forEach(b => b.classList.toggle("on", b.dataset.tab === t));
  render();
}

function render() {
  ({ today, ask: askView, network: networkView })[S.tab]();
}

document.addEventListener("click", e => {
  const t = e.target.closest("[data-tab],[data-act]");
  if (!t) return;
  if (t.dataset.tab) return setTab(t.dataset.tab);
  const a = t.dataset.act;
  if (a === "hours") { S.note = ""; S.manual = true; S.hours = +t.dataset.h; ls.set("hours", S.hours); today(); }
  else if (a === "research" || a === "open-research") research(t.dataset.t);
  else if (a === "person") personSheet(t.dataset.id);
  else if (a === "ask") { closeSheet(); doAsk(t.dataset.q); }
  else if (a === "tab") setTab(t.dataset.t);
  else if (a === "theme") { S.theme = t.dataset.t; networkView(); }
  else if (a === "cat") { const c = t.dataset.c; S.cats = S.cats.includes(c) ? S.cats.filter(x => x !== c) : [...S.cats, c]; t.classList.toggle("on"); }
});

function applyMode() {
  document.documentElement.dataset.theme = S.mode;
  $("#mode").setAttribute("aria-label", S.mode === "dark" ? "Switch to light mode" : "Switch to dark mode");
  const tc = document.getElementById("theme-color");
  if (tc) tc.content = S.mode === "light" ? "#ffffff" : "#0c0f17";
}

$("#mode").onclick = () => {
  S.mode = S.mode === "dark" ? "light" : "dark";
  ls.set("mode_v2", S.mode);
  applyMode();
};

function showProvenance() {
  const pCount = (S.meta && S.meta.portfolio) ? S.meta.portfolio.length : 17;
  const isPxLive = S.meta && S.meta.freshness && S.meta.freshness.prices === "live";
  openSheet(`
    <h3 class="sheet-title">Data Architecture & Status</h3>
    <p class="sub mb-3">FINN fuses live public market feeds with structured fundamental models and a privacy-preserving synthetic network layer.</p>
    <div class="provenance-grid">
      <div class="provenance-item">
        <div class="prov-status live">&#10003; LIVE EOD FEED</div>
        <b>Prices & Volumes (${pCount} Stocks)</b>
        <p class="sub">Real daily closing prices and volume series fetched via Yahoo Finance (yfinance) for all 17 NSE portfolio stocks. Drives unusual volume spikes (&ge;2&times; 20d avg) and intraday sparklines.</p>
      </div>
      <div class="provenance-item">
        <div class="prov-status live">&#10003; STANDARDIZED DISCLOSURES</div>
        <b>Exchange Filings</b>
        <p class="sub">Corporate announcements classified into reference glossary categories (Results, Management Changes, Capex, M&A, Litigation, Dividends).</p>
      </div>
      <div class="provenance-item">
        <div class="prov-status">&#128196; PRIMARY SOURCES</div>
        <b>Fundamentals & Concall Guidance</b>
        <p class="sub">Multi-quarter P&L (Revenue, EBITDA margin, PAT), balance sheets, and narrative-vs-numbers guidance delivery scorecards.</p>
      </div>
      <div class="provenance-item">
        <div class="prov-status">&#128274; PRIVACY-PRESERVING</div>
        <b>Network Layer (32 Profiles)</b>
        <p class="sub">Realistic mock executive profiles with career paths, alma maters, and relationship strengths. (Synthetic by design per ENAM challenge privacy guidelines — no unauthorized scraping of private LinkedIn data).</p>
      </div>
    </div>
    <div class="sheet-actions mt-3">
      <button class="btn btn-block primary" id="refreshPricesBtn"><svg class="btn-icon" viewBox="0 0 24 24"><path d="M23 4v6h-6M1 20v-6h6"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>Fetch Fresh EOD Market Data</button>
      <button class="btn btn-block mt-2" onclick="closeSheet()">Close</button>
    </div>
  `);
  const rf = $("#refreshPricesBtn");
  if (rf) {
    rf.onclick = async () => {
      rf.disabled = true;
      rf.innerHTML = `<div class="spinner-sm"></div> Contacting market data adapter...`;
      try {
        const res = await api("/api/refresh", { method: "POST" });
        rf.innerHTML = `&#10003; Updated ${res.prices?.tickers?.length || 17} symbols successfully!`;
        setTimeout(() => { closeSheet(); today(); }, 1000);
      } catch (err) {
        rf.innerHTML = `Snapshot feed active (${esc(err.message)})`;
        rf.disabled = false;
      }
    };
  }
}

$("#gear").onclick = settings;
if ($("#provBtn")) $("#provBtn").onclick = showProvenance;
applyMode();

(async () => {
  S.meta = await api("/api/meta");
  render();
})();
