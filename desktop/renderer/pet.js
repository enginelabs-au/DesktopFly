/**
 * Minimal transparent pet renderer. Presentation only; pose comes from main.
 */

const canvas = document.getElementById("fly");
const ctx = canvas.getContext("2d");

function drawFly(pose, scale) {
  const w = canvas.width;
  const h = canvas.height;
  ctx.clearRect(0, 0, w, h);
  if (pose && pose.visible === false) return;
  const s = Number.isFinite(scale) ? scale : 1;
  const cx = w / 2;
  const cy = h / 2;
  const heading = pose?.headingRad || 0;
  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(heading);
  ctx.scale(s, s);
  ctx.fillStyle = "rgba(24, 24, 24, 0.92)";
  ctx.beginPath();
  ctx.ellipse(0, 0, 18, 10, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "rgba(60, 60, 60, 0.55)";
  ctx.beginPath();
  ctx.ellipse(-6, -8, 10, 4, -0.4, 0, Math.PI * 2);
  ctx.ellipse(-6, 8, 10, 4, 0.4, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
}

function beat() {
  if (window.flyDesktop?.beatHostLease) window.flyDesktop.beatHostLease();
}

if (window.flyDesktop?.onPoseFrame) {
  window.flyDesktop.onPoseFrame((frame) => {
    drawFly(frame.pose, 1 - 0.35 * (frame.pose?.depth01 || 0));
  });
} else {
  drawFly({ headingRad: 0, depth01: 0 }, 1);
}

setInterval(beat, 100);
beat();
