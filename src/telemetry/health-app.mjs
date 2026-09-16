import { buildHealthDashboard } from "./health-dashboard.mjs";

function render(view) {
  document.getElementById("title").textContent = view.title;
  document.getElementById("disclaimer").textContent = view.disclaimer;
  document.getElementById("explanation").textContent = view.explanation;
  document.getElementById("doing").textContent = `What the system is doing: ${view.doing}`;
  document.getElementById("operator-action").textContent = `What you need to do: ${view.operator_action}`;
  const quiet = document.getElementById("quiet-note");
  if (view.quiet_note) {
    quiet.hidden = false;
    quiet.textContent = view.quiet_note;
  } else {
    quiet.hidden = true;
  }
  const cards = document.getElementById("cards");
  cards.innerHTML = "";
  for (const [key, value] of Object.entries(view.cards)) {
    const el = document.createElement("div");
    el.className = "card";
    el.innerHTML = `<strong>${key.replaceAll("_", " ")}</strong><span>${value}</span>`;
    cards.appendChild(el);
  }
  document.getElementById("technical").textContent = JSON.stringify(view.technical, null, 2);
}

const seed = {
  lifecycle: "RUNNING",
  quiet: false,
  health: {
    technical: {
      source: "local-seed",
      real_graph_enabled: true,
      connectome_mode: true,
      motion_driver: "connectome-lif",
      graph_source: "malecns-reviewed-subset",
      neuron_count: 4,
      synapse_count: 4,
    },
  },
};

render(buildHealthDashboard(seed));

window.desktopflyHealth = { render, buildHealthDashboard };
