const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));

const state = {
  left: null,
  right: null,
};

function showNotice(msg) {
  const el = $("#voteNotice");
  el.textContent = msg;
  el.classList.toggle("hidden", !msg);
}

async function fetchJSON(url, options) {
  const resp = await fetch(url, options);
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    const err = data?.detail || resp.statusText;
    throw new Error(err);
  }
  return data;
}

async function loadSongs() {
  const songs = await fetchJSON("/api/songs");
  const list = $("#songList");
  list.innerHTML = "";
  songs.forEach((s) => {
    const li = document.createElement("li");
    li.className = "list-item";
    li.innerHTML = `
      <span>${s.name}</span>
      <span class="muted">${s.wins}/${s.appearances} wins</span>
      <button class="danger" data-name="${s.name}">Remove</button>
    `;
    li.querySelector("button").addEventListener("click", async () => {
      try {
        await fetchJSON(`/api/songs/${encodeURIComponent(s.name)}`, { method: "DELETE" });
        await refreshAll();
      } catch (err) {
        alert(err.message);
      }
    });
    list.appendChild(li);
  });
}

async function addSong() {
  const input = $("#newSongInput");
  const name = input.value.trim();
  if (!name) return;
  try {
    await fetchJSON("/api/songs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    });
    input.value = "";
    await refreshAll();
  } catch (err) {
    alert(err.message);
  }
}

function setVoteButtonsEnabled(enabled) {
  $$("#vote .primary").forEach((b) => (b.disabled = !enabled));
}

async function loadPair() {
  try {
    setVoteButtonsEnabled(false);
    const pair = await fetchJSON("/api/pair");
    state.left = pair[0];
    state.right = pair[1];
    $("#leftName").textContent = state.left;
    $("#rightName").textContent = state.right;
    showNotice("");
    setVoteButtonsEnabled(true);
  } catch (err) {
    showNotice(err.message || "Add at least two songs to start voting.");
  }
}

async function submitVote(winner, loser) {
  try {
    setVoteButtonsEnabled(false);
    await fetchJSON("/api/vote", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ selected: winner, other: loser }),
    });
    await Promise.all([loadPair(), loadLeaderboard(), loadSongs()]);
  } catch (err) {
    alert(err.message);
  } finally {
    setVoteButtonsEnabled(true);
  }
}

async function loadLeaderboard() {
  const rows = await fetchJSON("/api/leaderboard");
  const tbody = $("#lbTable tbody");
  tbody.innerHTML = "";
  rows.forEach((r, idx) => {
    const tr = document.createElement("tr");
    const rate = (r.winRate * 100).toFixed(1) + "%";
    tr.innerHTML = `
      <td>${idx + 1}</td>
      <td>${r.name}</td>
      <td>${rate}</td>
      <td>${r.wins}</td>
      <td>${r.appearances}</td>
    `;
    tbody.appendChild(tr);
  });
}

async function refreshAll() {
  await Promise.all([loadSongs(), loadPair(), loadLeaderboard()]);
}

function init() {
  $("#addSongBtn").addEventListener("click", addSong);
  $("#newSongInput").addEventListener("keydown", (e) => {
    if (e.key === "Enter") addSong();
  });
  $("#leftVoteBtn").addEventListener("click", () => submitVote(state.left, state.right));
  $("#rightVoteBtn").addEventListener("click", () => submitVote(state.right, state.left));
  $("#refreshLbBtn").addEventListener("click", loadLeaderboard);

  refreshAll();
}

document.addEventListener("DOMContentLoaded", init);
