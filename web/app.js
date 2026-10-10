"use strict";

(() => {
  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => [...document.querySelectorAll(selector)];
  const state = { session: null, brief: null, mission: null, records: [], analystToken: null, responderToken: null, response: null, collector: null, dirty: false, hintLevel: 0, ready: false, currentView: "guild", storySeen: false, requestBusy: false, initialised: false };
  let toastTimeout;

  const make = (tag, text, className) => {
    const element = document.createElement(tag);
    if (text !== undefined && text !== null) element.textContent = String(text);
    if (className) element.className = className;
    return element;
  };
  const replace = (node, children) => node.replaceChildren(...children);
  const plainError = (data, fallback) => typeof data?.error === "string" ? data.error : (data?.error?.message || data?.message || fallback);
  const evidenceLabel = (saved) => {
    if (saved.kind === "clue") return "Guild message and matching slide";
    const reference = String(saved.label || "").match(/(?:dossiers\/|dossier\s+)(\d+)/i)?.[1];
    if (reference) return saved.kind === "restricted-dossier" ? `Record CL-${reference} outside your permissions` : `Actual response from record CL-${reference}`;
    return "Saved server response";
  };
  const readableCheck = (check) => {
    const explanations = {
      original: ["The story's restricted record was refused to your analyst account.", "The story's restricted record was not refused in the required way. Ask Codex to review this failed check."],
      variant: ["A second record behind the same permission boundary was also refused.", "Another record behind the same boundary was not refused in the required way."],
      authorised: ["Your own permitted record still opens correctly.", "Your permitted record did not open correctly. The repair must preserve normal access."],
      "filtered-list": ["The record list contains only the two records permitted for your account.", "The record list did not match your account's permitted records."],
      collector: ["The message feed refused a new fictional event. Earlier saved events remain.", "The check did not establish that the message feed was switched off and new events were refused."],
      "source-fresh": ["The running server uses the current saved code.", "The code was changed after the server started. Ask Codex to restart it with the same investigation data, then repeat these checks."]
    };
    return explanations[check.key]?.[check.passed ? 0 : 1] || check.explanation;
  };
  const readableCheckTitle = (check) => {
    const labels = {
      original: ["The story's restricted record is blocked", "The story's restricted record still needs protection"],
      variant: ["The same rule protects a second record", "The second record still needs protection"],
      authorised: ["Your permitted record still opens", "Your permitted record needs attention"],
      "filtered-list": ["Your list stays within its permissions", "Your record list needs attention"],
      collector: ["New messages are refused", "The message feed still needs checking"],
      "source-fresh": ["The running lab matches its saved code", "Codex needs to restart the lab before checking"]
    };
    return labels[check.key]?.[check.passed ? 0 : 1] || check.label;
  };
  const readableTask = (task) => ({
    "Preserve one real restricted dossier response from your investigation.": "Save one actual response that shows a story record outside your account's permissions.",
    "Complete the defensive verification with the operator.": "After reviewing your finding with Codex, run the responder protection checks.",
    "Revoke the mock collector credential and repeat verification.": "Switch off the message feed and run the protection checks again."
  }[task] || task);
  const notify = (message) => {
    const toast = $("#toast");
    toast.textContent = message;
    toast.hidden = false;
    clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => { toast.hidden = true; }, 4200);
  };
  const feedback = (selector, message, kind = "") => {
    const target = $(selector);
    target.textContent = message;
    target.className = `inline-status ${kind}`;
  };

  async function request(path, { method = "GET", body, role = "analyst" } = {}) {
    const headers = { Accept: "application/json" };
    const token = role === "responder" ? state.responderToken : role === "public" ? null : state.analystToken;
    if (token) headers.Authorization = `Bearer ${token}`;
    if (body !== undefined) headers["Content-Type"] = "application/json";
    let response;
    try {
      response = await fetch(path, { method, headers, ...(body !== undefined ? { body: JSON.stringify(body) } : {}), cache: "no-store" });
    } catch (_) {
      throw new Error("The local lab did not answer. Check that the training server is running, then try again.");
    }
    let data;
    try { data = await response.json(); }
    catch (_) { throw new Error("The local lab returned an unreadable answer. Ask Codex to check the server before continuing."); }
    return { ok: response.ok, status: response.status, data, path, method };
  }
  async function requireRequest(path, options) {
    const response = await request(path, options);
    if (!response.ok) throw new Error(plainError(response.data, `The request could not be completed (status ${response.status}).`));
    return response.data;
  }

  function renderMode() {
    let label = "Lab not connected";
    if (state.session) {
      const training = state.session.mode === "training-vulnerable";
      label = training ? "Training mode · flaw enabled" : "Protected mode · run checks";
    }
    $$('[data-mode]').forEach((badge) => { badge.textContent = label; });
  }
  function setConnectionError(message) {
    const banner = $("#connection-banner");
    const text = make("span", message);
    const retry = make("button", "Reconnect to the local lab", "button button-outline");
    retry.addEventListener("click", () => bootstrap());
    replace(banner, [text, retry]);
    banner.hidden = false;
  }
  function setReady(ready) {
    state.ready = ready;
    ["#save-clue", "#open-record", "#save-notes", "#unlock-responder"].forEach((selector) => { $(selector).disabled = !ready; });
  }

  function selectView(name, { focus = false, setHash = true } = {}) {
    if (!["guild", "civiclens", "watchtower"].includes(name)) name = "guild";
    state.currentView = name;
    $$("[data-tab]").forEach((tab) => {
      const active = tab.dataset.tab === name;
      tab.setAttribute("aria-selected", String(active));
      tab.tabIndex = active ? 0 : -1;
    });
    $$(".view-panel").forEach((panel) => { panel.hidden = panel.id !== `panel-${name}`; });
    if (name !== "guild") state.storySeen = true;
    if (setHash && location.hash !== `#${name}`) history.replaceState(null, "", `#${name}`);
    renderProgress();
    if (focus) $("#main-content").focus({ preventScroll: true });
  }
  function renderProgress() {
    const evidence = state.mission?.evidence || [];
    const notes = latestNotes();
    const stages = {
      story: state.storySeen || evidence.some((item) => item.kind === "clue"),
      records: evidence.some((item) => item.kind !== "clue"),
      notes: Boolean(notes.observation?.trim() && notes.hypothesis?.trim()),
      defence: state.mission?.outcome?.key === "victory"
    };
    const next = Object.keys(stages).find((key) => !stages[key]);
    $$("[data-step]").forEach((step, index) => {
      const done = stages[step.dataset.step];
      step.classList.toggle("done", done);
      step.classList.toggle("current", !done && step.dataset.step === next);
      step.querySelector(".step-number").textContent = done ? "✓" : String(index + 1);
      if (step.dataset.step === next) step.setAttribute("aria-current", "step");
      else step.removeAttribute("aria-current");
    });
  }

  function renderBrief() {
    const brief = state.brief;
    const messages = (brief.messages || []).map((message) => {
      const item = make("article", null, "guild-message");
      const avatar = make("div", (message.author || "?").slice(0, 1), "avatar");
      avatar.setAttribute("aria-hidden", "true");
      const content = make("div");
      const author = make("div", null, "message-author");
      author.append(make("span", message.author || "Guild member"), make("span", message.time || "", "message-time"), make("span", `# ${message.channel || "guild"}`, "message-channel"));
      content.append(author, make("p", message.text, "message-text"));
      item.append(avatar, content);
      return item;
    });
    const intro = make("div", null, "guild-story-context");
    intro.append(make("p", "NextVoice is a fictional youth rights group. It questions public authorities buying systems that monitor young people's political activity. Some members play together in this guild. Gallantir, the company selling CivicLens, wants to anticipate their objections."));
    intro.append(make("p", "In this story, procurement means buying these monitoring systems. A raid is a cooperative game mission; a wipe means the team loses and tries again.", "story-vocabulary"));
    replace($("#message-list"), [intro, ...messages]);
    $("#slide-title").textContent = brief.slide?.title || "CivicLens presentation";
    $("#slide-quote").textContent = brief.slide?.quote ? `“${brief.slide.quote}”` : "No presentation quote was supplied.";
    $("#slide-source").textContent = brief.slide?.source_ref || "Reference not supplied";
    $("#slide-claim").textContent = brief.slide?.claim || "Compare this slide with the guild conversation.";
    const glossary = $("#glossary-list");
    const baseTerms = new Set([...glossary.querySelectorAll("dt")].map((node) => node.textContent));
    for (const term of brief.glossary || []) {
      if (!baseTerms.has(term.term)) { glossary.append(make("dt", term.term), make("dd", term.meaning)); baseTerms.add(term.term); }
    }
    if (!baseTerms.has("AI helpers")) glossary.append(make("dt", "AI helpers"), make("dd", "Independent AI reviewers that check whether the evidence supports your finding. Codex may call them red team agents."));
    if (!baseTerms.has("Blue team")) glossary.append(make("dt", "Blue team"), make("dd", "The helper that repairs the server and then checks the protection."));
  }

  function renderAccount() {
    const analyst = state.session?.analyst;
    if (!analyst) return;
    $("#account-name").textContent = analyst.display_name || "Your training account";
    const ids = analyst.allowed_dossier_ids || [];
    $("#account-scope").textContent = `Your account is allowed to see ${ids.map((id) => `CL-${id}`).join(" and ")}. Other records belong to different workspaces, which are separate groups of information.`;
  }
  function renderRecords() {
    const cards = state.records.map((record) => {
      const button = make("button", null, "dossier-card");
      button.type = "button";
      button.setAttribute("aria-label", `Open record ${record.id}: ${record.title}`);
      const callToAction = make("span", null, "record-open");
      callToAction.append(make("span", "Open this record"), make("span", "→"));
      button.append(make("span", `CL-${record.id}`, "record-id"), make("strong", record.title), make("p", record.summary), callToAction);
      button.addEventListener("click", () => { $("#record-reference").value = record.id; openRecord(record.id); });
      return button;
    });
    replace($("#dossier-list"), cards.length ? cards : [make("p", "No records are available for this account.", "loading-copy")]);
  }

  function latestNotes() {
    const notes = state.mission?.notes;
    if (Array.isArray(notes)) return notes[notes.length - 1] || {};
    return notes || {};
  }
  function renderMission() {
    const mission = state.mission;
    if (!mission) return;
    const evidence = mission.evidence || [];
    $("#evidence-count").textContent = String(evidence.length);
    if (evidence.length) {
      replace($("#saved-evidence"), evidence.map((saved) => {
        const item = make("div", null, "evidence-item");
        const description = make("div");
        description.append(make("strong", evidenceLabel(saved)), make("small", saved.kind === "clue" ? "Story clue" : "Actual server response"));
        item.append(make("span", "✓"), description);
        return item;
      }));
    } else {
      const empty = make("div", null, "empty-evidence");
      empty.append(make("span", "⌑"), make("p", "No evidence saved yet. Your first clue is in CivicLens."));
      replace($("#saved-evidence"), [empty]);
    }
    const notes = latestNotes();
    if (!state.dirty) {
      $("#observation").value = notes.observation || "";
      $("#hypothesis").value = notes.hypothesis || "";
      $("#notes-state").textContent = notes.observation || notes.hypothesis ? "Saved to the lab" : "Not saved yet";
      $("#notes-state").classList.remove("unsaved");
    }
    const hints = (mission.assistance || []).filter((item) => item.kind === "hint");
    state.hintLevel = Math.max(0, ...hints.map((hint) => Number(hint.level) || 0));
    renderHints();
    const outcome = mission.outcome || { key: "incomplete", title: "The investigation is still open", explanation: "Read the story, save evidence and write your findings. Defence results will appear after real checks run.", remaining: [] };
    $("#verification-panel").className = `verification-panel ${["victory", "false-victory", "raid-wipes"].includes(outcome.key) ? outcome.key : ""}`;
    $("#outcome-title").textContent = outcome.title;
    $("#outcome-explanation").textContent = outcome.explanation;
    replace($("#outcome-remaining"), (outcome.remaining || []).map((item) => make("li", readableTask(item))));
    const verification = mission.verification;
    const checks = verification?.checks || [];
    replace($("#verification-checks"), checks.map((check) => {
      const item = make("div", null, `verification-check ${check.passed ? "passed" : ""}`);
      const content = make("div");
      content.append(make("strong", readableCheckTitle(check)), make("p", readableCheck(check)));
      item.append(make("span", check.passed ? "✓" : "!"), content);
      return item;
    }));
    $("#verification-technical").hidden = !verification;
    if (verification) $("#verification-json").textContent = JSON.stringify(verification, null, 2);
    renderProgress();
  }
  async function refreshMission() {
    state.mission = await requireRequest("/api/mission/status");
    renderMission();
  }

  const hintText = [
    "Compare the exact words on the CivicLens slide with the guild messages. Which member said them first? What does that tell you, and what does it still leave unanswered?",
    "Read the sentence that begins ‘Your account is allowed to see…’. Open one of those records and compare it with the information on the slide. Is the slide's reference part of your account's permitted list?",
    "The slide has a reference beginning with CL-. The digits after CL- can go in ‘Record reference’. Try only that story-linked reference and look closely at the actual response.",
    "Compare the returned record with your account's allowed list. If you see information outside that list, save this one response and stop. Explain what you saw in your own words. The record's source labels may help you trace how the quote arrived."
  ];
  function renderHints() {
    replace($("#hint-list"), hintText.slice(0, state.hintLevel).map((hint) => make("li", hint)));
    const button = $("#next-hint");
    if (state.hintLevel >= hintText.length) {
      button.textContent = "All hints are open";
      button.disabled = true;
    } else {
      button.textContent = state.hintLevel ? "Show the next hint +" : "Show the first hint +";
      button.disabled = !state.ready;
    }
  }

  async function bootstrap() {
    setReady(false);
    $("#connection-banner").hidden = true;
    try {
      state.session = await requireRequest("/api/session", { role: "public" });
      if (!state.session.analyst?.token) throw new Error("The lab has not supplied a training account. Ask Codex to check the server.");
      state.analystToken = state.session.analyst.token;
      const results = await Promise.all([
        requireRequest("/api/brief", { role: "public" }),
        requireRequest("/api/dossiers"),
        requireRequest("/api/mission/status")
      ]);
      state.brief = results[0];
      state.records = results[1].items || [];
      state.mission = results[2];
      setReady(true);
      renderBrief(); renderAccount(); renderRecords(); renderMode(); renderMission();
      if (!state.initialised) { selectView(location.hash.slice(1) || "guild", { setHash: false }); state.initialised = true; }
    } catch (error) { renderMode(); setConnectionError(error.message); renderHints(); }
  }

  async function saveEvidence(body, button) {
    button.disabled = true;
    const initialText = button.textContent;
    button.textContent = "Saving…";
    try {
      const saved = await requireRequest("/api/evidence", { method: "POST", body });
      await refreshMission();
      notify(`Saved: ${saved.saved ? evidenceLabel(saved.saved) : "evidence"}.`);
    } catch (error) { notify(error.message); }
    finally { button.textContent = initialText; button.disabled = !state.ready; }
  }

  async function openRecord(reference) {
    if (!state.ready || state.requestBusy) return;
    if (!Number.isInteger(Number(reference)) || Number(reference) < 1 || Number(reference) > 999999) {
      $("#record-reference").reportValidity(); return;
    }
    state.requestBusy = true;
    $("#open-record").disabled = true;
    $("#open-record").textContent = "Requesting…";
    $("#save-record").hidden = true;
    try {
      const result = await request(`/api/dossiers/${Number(reference)}`);
      state.response = result;
      renderResponse(Number(reference), result);
    } catch (error) {
      state.response = null;
      const panel = $("#record-response");
      panel.hidden = false; panel.className = "record-response error";
      $("#response-symbol").textContent = "!";
      $("#response-heading").textContent = "The local lab did not return a response";
      $("#response-explanation").textContent = error.message;
      replace($("#record-content"), []); replace($("#record-request-meta"), []);
      $("#record-json").textContent = "No server response was received.";
    } finally {
      state.requestBusy = false;
      $("#open-record").disabled = !state.ready;
      $("#open-record").textContent = "Open record →";
    }
  }
  function renderResponse(reference, result) {
    const panel = $("#record-response");
    const permitted = (state.session?.analyst?.allowed_dossier_ids || []).includes(reference);
    const dossier = result.data?.dossier;
    panel.hidden = false;
    panel.className = `record-response ${result.ok ? permitted ? "" : "error" : result.status === 403 ? "denied" : "error"}`;
    $("#response-symbol").textContent = result.ok ? permitted ? "✓" : "!" : result.status === 403 ? "◇" : "!";
    if (result.ok) {
      $("#response-heading").textContent = permitted ? "The server returned an allowed record" : "The server returned a record outside your account's permissions";
      $("#response-explanation").textContent = permitted ? `CL-${reference} is on your account's allowed list. This is the normal behaviour to compare with your next observation.` : `CL-${reference} is not on your account's allowed list, yet the server returned it. Save this response and describe what you see. A response is evidence; it is not yet a complete explanation.`;
    } else if (result.status === 403) {
      $("#response-heading").textContent = "The server refused access to this record";
      $("#response-explanation").textContent = "Your account was recognised, but it is not allowed to read this record. This is the expected boundary for a restricted record. Continue with the full protection checks before concluding that the mission is complete.";
    } else if (result.status === 404) {
      $("#response-heading").textContent = "The requested record does not exist";
      $("#response-explanation").textContent = "Check the digits in the story reference. A missing record is different from a permission rule blocking access.";
    } else if (result.status === 401) {
      $("#response-heading").textContent = "The server could not recognise this account";
      $("#response-explanation").textContent = "The training account could not be checked. Reconnect to the lab or ask Codex to check it. This does not prove a permission repair.";
    } else {
      $("#response-heading").textContent = "The request could not be completed";
      $("#response-explanation").textContent = plainError(result.data, `The local server returned status ${result.status}.`);
    }
    const children = [];
    if (dossier) {
      const heading = make("div", null, "record-content-header");
      heading.append(make("h4", dossier.title), make("p", dossier.summary));
      children.push(heading);
      const fields = make("div", null, "record-fields");
      for (const [label, value] of [["Reference", `CL-${dossier.id}`], ["Information group (workspace)", dossier.workspace], ["About", dossier.subject]]) {
        if (value) { const field = make("div"); field.append(make("strong", label), make("span", value)); fields.append(field); }
      }
      children.push(fields);
      for (const record of dossier.records || []) {
        const entry = make("div", null, "record-entry");
        entry.append(make("strong", record.label), make("p", record.text));
        children.push(entry);
      }
    }
    replace($("#record-content"), children);
    const stopRule = make("p", "One unexpected record is enough. Save it and discuss it with Codex before opening other restricted records.", "evidence-stop-rule");
    if (!permitted && result.ok) $("#record-content").append(stopRule);
    $("#save-record").hidden = !result.data?.request_id;
    $("#save-record").disabled = !state.ready;
    const meta = make("div", null, "request-meta");
    meta.append(make("span", `${result.method} ${result.path}`), make("span", `Status ${result.status}`), make("span", `Request ${result.data?.request_id || "not supplied"}`));
    replace($("#record-request-meta"), [meta]);
    $("#record-json").textContent = JSON.stringify(result.data, null, 2);
    panel.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function renderCollector() {
    const collector = state.collector;
    if (!collector) return;
    $("#collector-state").textContent = collector.active ? `Message feed is active. ${collector.event_count} fictional event${collector.event_count === 1 ? "" : "s"} stored.` : `Message feed is switched off. ${collector.event_count} previously stored fictional event${collector.event_count === 1 ? " remains" : "s remain"}. Switching off the feed does not erase earlier evidence.`;
    $("#revoke-collector").disabled = !collector.active;
    $("#revoke-collector").textContent = collector.active ? "Switch off the message feed" : "Message feed is switched off";
  }
  async function refreshCollector() {
    state.collector = await requireRequest("/api/collector/status", { role: "responder" });
    renderCollector();
  }
  async function defenceAction(button, action) {
    button.disabled = true;
    try { await action(); }
    catch (error) { feedback("#collector-feedback", error.message, "error"); }
    finally { button.disabled = false; renderCollector(); }
  }

  $$("[data-tab]").forEach((tab, index, tabs) => {
    tab.addEventListener("click", () => selectView(tab.dataset.tab));
    tab.addEventListener("keydown", (event) => {
      let next;
      if (event.key === "ArrowRight") next = (index + 1) % tabs.length;
      if (event.key === "ArrowLeft") next = (index - 1 + tabs.length) % tabs.length;
      if (event.key === "Home") next = 0;
      if (event.key === "End") next = tabs.length - 1;
      if (next !== undefined) { event.preventDefault(); selectView(tabs[next].dataset.tab); tabs[next].focus(); }
    });
  });
  $$('[data-go]').forEach((button) => button.addEventListener("click", () => selectView(button.dataset.go, { focus: true })));
  window.addEventListener("hashchange", () => selectView(location.hash.slice(1), { setHash: false }));
  $("#show-help").addEventListener("click", () => {
    const open = $("#beginner-help").hidden;
    $("#beginner-help").hidden = !open;
    $("#show-help").setAttribute("aria-expanded", String(open));
  });
  $("#focus-notebook").addEventListener("click", () => { $("#observation").focus(); });
  $$('[data-focus-notebook]').forEach((button) => button.addEventListener("click", () => { $("#observation").focus(); }));
  $("#save-clue").addEventListener("click", () => saveEvidence({ kind: "clue" }, $("#save-clue")));
  $("#record-form").addEventListener("submit", (event) => { event.preventDefault(); openRecord(Number($("#record-reference").value)); });
  $("#save-record").addEventListener("click", () => { if (state.response?.data?.request_id) saveEvidence({ request_id: state.response.data.request_id }, $("#save-record")); });
  ["#observation", "#hypothesis"].forEach((selector) => $(selector).addEventListener("input", () => {
    state.dirty = true;
    $("#notes-state").textContent = "Unsaved changes";
    $("#notes-state").classList.add("unsaved");
    feedback("#notes-feedback", "");
  }));
  $("#notes-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const observation = $("#observation").value.trim();
    const hypothesis = $("#hypothesis").value.trim();
    if (!observation || !hypothesis) { feedback("#notes-feedback", "Add a short observation and an explanation, even if your explanation is ‘I am not sure yet’.", "error"); return; }
    const button = $("#save-notes");
    button.disabled = true;
    const submitted = { observation, hypothesis };
    try {
      await requireRequest("/api/notes", { method: "POST", body: submitted });
      // Keep any edits made while the save request was running.
      state.dirty = $("#observation").value.trim() !== submitted.observation || $("#hypothesis").value.trim() !== submitted.hypothesis;
      await refreshMission();
      feedback("#notes-feedback", state.dirty ? "Your submitted notes were saved. The newer changes still need saving." : "Your notes are saved. You can discuss this evidence with Codex.", "success");
    } catch (error) { feedback("#notes-feedback", `Notes were not confirmed saved. ${error.message}`, "error"); }
    finally { button.disabled = !state.ready; }
  });
  $("#next-hint").addEventListener("click", async () => {
    if (!state.ready || state.hintLevel >= hintText.length) return;
    const button = $("#next-hint");
    button.disabled = true;
    try {
      await requireRequest("/api/mission/assistance", { method: "POST", body: { kind: "hint", level: state.hintLevel + 1 } });
      state.hintLevel += 1;
      renderHints();
    } catch (error) { notify(`Hint use could not be recorded. ${error.message}`); button.disabled = false; }
  });
  $("#responder-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = $("#unlock-responder");
    button.disabled = true;
    const previousToken = state.responderToken;
    state.responderToken = $("#responder-code").value.trim();
    try {
      await refreshCollector();
      $("#defence-controls").hidden = false;
      $("#responder-code").value = "";
      feedback("#responder-feedback", "Code accepted by the actual server. The responder controls are now available.", "success");
    } catch (error) {
      state.responderToken = previousToken;
      feedback("#responder-feedback", `The server did not accept that responder code. ${error.message}`, "error");
    } finally { button.disabled = !state.ready; }
  });
  $("#simulate-event").addEventListener("click", () => defenceAction($("#simulate-event"), async () => {
    const result = await requireRequest("/api/collector/simulate", { method: "POST", role: "responder" });
    await refreshCollector();
    if (result.accepted) {
      feedback("#collector-feedback", "The message feed accepted the fictional test event. New activity can still enter CivicLens.");
    } else if ([401, 403].includes(result.status)) {
      feedback("#collector-feedback", "The message feed refused the fictional test event. This confirms that new activity was blocked in this check.", "success");
    } else {
      feedback("#collector-feedback", "This test could not confirm the message feed's protection. Refresh the state and ask Codex to check the server before drawing a conclusion.", "error");
    }
    await refreshMission();
  }));
  $("#revoke-collector").addEventListener("click", () => defenceAction($("#revoke-collector"), async () => {
    await requireRequest("/api/collector/revoke", { method: "POST", role: "responder" });
    await refreshCollector();
    feedback("#collector-feedback", "The server has switched off this message feed. Test it again to check that a new event is refused.", "success");
    await refreshMission();
  }));
  $("#verify-mission").addEventListener("click", async () => {
    const button = $("#verify-mission");
    button.disabled = true;
    feedback("#verify-feedback", "The server is running the actual protection checks…");
    try {
      await requireRequest("/api/mission/verify", { method: "POST", role: "responder" });
      state.session = await requireRequest("/api/session", { role: "public" });
      await refreshCollector(); await refreshMission(); renderMode();
      feedback("#verify-feedback", "Checks finished. Read the verified outcome below; passing one check alone does not complete the mission.");
    } catch (error) { feedback("#verify-feedback", `Checks could not be confirmed. ${error.message}`, "error"); }
    finally { button.disabled = false; }
  });
  $("#refresh-status").addEventListener("click", async () => {
    const button = $("#refresh-status"); button.disabled = true;
    try {
      state.session = await requireRequest("/api/session", { role: "public" });
      await refreshCollector(); await refreshMission(); renderMode();
      feedback("#verify-feedback", "Actual lab state refreshed. To test the protection after a code repair, run the protection checks.");
    } catch (error) { feedback("#verify-feedback", error.message, "error"); }
    finally { button.disabled = false; }
  });
  $("#declare-victory").addEventListener("click", async () => {
    const button = $("#declare-victory"); button.disabled = true;
    try {
      await requireRequest("/api/mission/declaration", { method: "POST", body: { victory: true } });
      await refreshMission();
      feedback("#declaration-feedback", "Your conclusion is recorded as a claim. The verified outcome still depends on the actual checks.");
    } catch (error) { feedback("#declaration-feedback", error.message, "error"); }
    finally { button.disabled = false; }
  });
  window.addEventListener("beforeunload", (event) => { if (state.dirty) { event.preventDefault(); event.returnValue = ""; } });
  selectView(location.hash.slice(1) || "guild", { setHash: false });
  bootstrap();
})();
