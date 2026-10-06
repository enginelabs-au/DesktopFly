/**
 * Procedural transparent fly renderer. Presentation only; pose comes from main.
 *
 * Everything here is cosmetic drawing driven by the pose frame (speed,
 * heading, locomotion). It makes no claim about how a fly's body is
 * controlled: the tripod gait, folded/spread wings, and idle grooming are
 * authored animation, not neural output.
 */

const canvas = document.getElementById("fly");
const ctx = canvas.getContext("2d");
const TAU = Math.PI * 2;

const state = {
  frame: null,
  heading: 0,
  speed: 0,
  gaitPhase: 0,
  flight: 0, // 0 = wings folded, 1 = wings spread and beating
  wingPhase: 0,
  idleSinceMs: performance.now(),
  groomStartMs: 0,
  groomUntilMs: 0,
  nextGroomMs: performance.now() + 3000,
  lastMs: performance.now(),
};

const SKIN = "rgba(38, 31, 28, 0.98)";
const LEG = "rgba(22, 18, 17, 0.86)";

function angDiff(a, b) {
  return ((((a - b + Math.PI) % TAU) + TAU) % TAU) - Math.PI;
}

function lerp(a, b, t) {
  return a + (b - a) * t;
}

// Leg attachment (thorax) and resting foot positions in body space, +x forward.
const LEGS = [
  { attach: [17, 4.5], rest: [25, 13] }, // front
  { attach: [12, 5.5], rest: [13, 18] }, // middle
  { attach: [7, 4.5], rest: [0, 15] }, // hind
];

function drawLeg(idx, side, nowMs) {
  const leg = LEGS[idx];
  const moving = state.speed > 2;
  const strideAmp = Math.min(6.5, 1.5 + state.speed * 0.07);
  let footX = leg.rest[0];
  let footY = leg.rest[1];
  // Alternating tripod: front-left + middle-right + hind-left, then the rest.
  const group = side < 0 ? idx % 2 : (idx + 1) % 2;
  if (moving) {
    const phase = state.gaitPhase + group * Math.PI;
    footX += strideAmp * Math.sin(phase);
    const swing = Math.max(0, Math.cos(phase)); // foot lifted while swinging forward
    footY -= swing * 3.2;
  }
  // Front legs rub together during idle grooming.
  if (idx === 0 && nowMs < state.groomUntilMs && !moving) {
    const t = (nowMs - state.groomStartMs) / 1000;
    footX = 27 + 2.6 * Math.sin(t * TAU * 5.5 + (side > 0 ? 0 : Math.PI));
    footY = 3.2;
  }
  const ax = leg.attach[0];
  const ay = leg.attach[1];
  const kneeX = (ax + footX) / 2 - 1.5;
  const kneeY = (ay + footY) / 2 + 3.5;
  ctx.beginPath();
  ctx.moveTo(ax, side * ay);
  ctx.lineTo(kneeX, side * kneeY);
  ctx.lineTo(footX, side * footY);
  ctx.stroke();
  ctx.beginPath();
  ctx.arc(footX, side * footY, 0.9, 0, TAU);
  ctx.fillStyle = LEG;
  ctx.fill();
}

function drawWings() {
  const level = state.flight;
  const flutter = level * 0.2 * Math.sin(state.wingPhase);
  ctx.fillStyle = `rgba(174, 216, 231, ${lerp(0.3, 0.34, level)})`;
  ctx.strokeStyle = "rgba(112, 161, 180, 0.6)";
  ctx.lineWidth = 1;
  for (const side of [-1, 1]) {
    ctx.save();
    ctx.scale(1, side);
    ctx.rotate(lerp(0.08, -0.38, level) + flutter);
    ctx.beginPath();
    ctx.ellipse(
      lerp(-8, -3, level),
      lerp(-5, -13, level),
      lerp(21, 19, level),
      lerp(4.4, 6, level),
      lerp(0, -0.12, level),
      0,
      TAU,
    );
    ctx.fill();
    ctx.stroke();
    ctx.restore();
  }
}

function drawBody(nowMs) {
  // Striped abdomen.
  ctx.fillStyle = "rgba(45, 35, 28, 0.96)";
  ctx.beginPath();
  ctx.ellipse(-2, 0, 19, 10, 0, 0, TAU);
  ctx.fill();
  ctx.save();
  ctx.clip();
  ctx.fillStyle = "rgba(18, 16, 15, 0.8)";
  for (const x of [-12, -5, 2, 9]) ctx.fillRect(x, -11, 3, 22);
  ctx.restore();

  // Thorax and head.
  ctx.fillStyle = "rgba(58, 43, 34, 0.98)";
  ctx.beginPath();
  ctx.ellipse(13, 0, 9, 9, 0, 0, TAU);
  ctx.fill();
  ctx.fillStyle = SKIN;
  ctx.beginPath();
  ctx.ellipse(22, 0, 7, 7, 0, 0, TAU);
  ctx.fill();

  // Compound eyes.
  ctx.fillStyle = "rgba(137, 32, 41, 0.95)";
  ctx.beginPath();
  ctx.ellipse(24, -4, 3.5, 3.5, 0, 0, TAU);
  ctx.ellipse(24, 4, 3.5, 3.5, 0, 0, TAU);
  ctx.fill();

  // Antennae twitch slightly, more when still.
  const twitch = 0.12 * Math.sin(nowMs / 170) * (state.speed > 2 ? 0.4 : 1);
  ctx.strokeStyle = "rgba(22, 18, 17, 0.8)";
  ctx.lineWidth = 1.2;
  for (const side of [-1, 1]) {
    ctx.beginPath();
    ctx.moveTo(26, side * 3);
    ctx.quadraticCurveTo(34, side * (9 + twitch * 8), 36, side * (7 + twitch * 10));
    ctx.stroke();
  }
}

function draw(nowMs) {
  const w = canvas.width;
  const h = canvas.height;
  ctx.clearRect(0, 0, w, h);
  const pose = state.frame?.pose;
  if (pose && pose.visible === false) return;
  const depth = pose?.depth01 || 0;
  const s = (1 - 0.35 * depth) * 1.1;
  const speedNorm = Math.min(1, state.speed / 90);
  // Slight yaw sway and bob with each stride.
  const sway = state.speed > 2 ? 0.05 * speedNorm * Math.sin(state.gaitPhase * 2) : 0;

  ctx.save();
  ctx.translate(w / 2, h / 2);
  ctx.rotate(state.heading + sway);
  ctx.scale(s, s);

  ctx.strokeStyle = LEG;
  ctx.lineWidth = 1.5;
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  for (const side of [-1, 1]) {
    for (let idx = 0; idx < 3; idx += 1) drawLeg(idx, side, nowMs);
  }
  drawBody(nowMs);
  drawWings();
  ctx.restore();
}

function step(nowMs) {
  const dt = Math.min(0.05, Math.max(0.001, (nowMs - state.lastMs) / 1000));
  state.lastMs = nowMs;
  const pose = state.frame?.pose;
  if (pose) {
    // Smooth heading toward the latest pose (fast turns allowed, no snapping).
    const err = angDiff(pose.headingRad || 0, state.heading);
    const maxStep = 22 * dt;
    state.heading += Math.max(-maxStep, Math.min(maxStep, err));
    // Smooth speed so legs speed up and slow down instead of jumping.
    const target = pose.speedPointsS || 0;
    state.speed += (target - state.speed) * Math.min(1, dt * 14);
    state.flight += ((pose.locomotion === "flight" ? 1 : 0) - state.flight) * Math.min(1, dt * 12);
  }
  if (state.speed > 2) {
    const gaitHz = 3 + state.speed / 12;
    state.gaitPhase = (state.gaitPhase + TAU * gaitHz * dt) % (TAU * 100);
    state.idleSinceMs = nowMs;
    state.groomUntilMs = 0;
  } else if (nowMs > state.nextGroomMs && nowMs - state.idleSinceMs > 1500) {
    // Cosmetic idle grooming after standing still for a while.
    state.groomStartMs = nowMs;
    state.groomUntilMs = nowMs + 1200 + Math.random() * 800;
    state.nextGroomMs = state.groomUntilMs + 3000 + Math.random() * 5000;
  }
  state.wingPhase = (state.wingPhase + TAU * 38 * dt * (0.15 + 0.85 * state.flight)) % TAU;
  draw(nowMs);
  requestAnimationFrame(step);
}

function beat() {
  if (window.flyDesktop?.beatHostLease) window.flyDesktop.beatHostLease();
}

if (window.flyDesktop?.onPoseFrame) {
  window.flyDesktop.onPoseFrame((frame) => {
    state.frame = frame;
  });
}

requestAnimationFrame(step);
setInterval(beat, 100);
beat();
