/**
 * Procedural transparent fly renderer. Presentation only; pose comes from main.
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
  const contact = pose?.surfaceContact && pose.surfaceContact !== "none";
  const wing = contact ? 0.03 : 0.12 * Math.sin(Date.now() / 55);
  const stride = contact ? 0.2 * Math.sin(Date.now() / 90) : 0;

  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(heading);
  ctx.scale(s, s);

  // Legs are presentation-only and make bounded surface contact visible.
  ctx.strokeStyle = "rgba(22, 18, 17, 0.86)";
  ctx.lineWidth = 1.6;
  ctx.lineCap = "round";
  for (const side of [-1, 1]) {
    for (const offset of [-1, 0, 1]) {
      const y = side * (4 + offset * 4);
      ctx.beginPath();
      ctx.moveTo(-2 + offset * 3, y);
      ctx.lineTo(-11 + offset * 3, side * (13 + offset * 2) + stride);
      ctx.lineTo(-17 + offset * 2, side * (14 + offset * 2) + stride);
      ctx.stroke();
    }
  }

  // Clear wings sit behind the thorax.
  ctx.fillStyle = "rgba(174, 216, 231, 0.38)";
  ctx.strokeStyle = "rgba(112, 161, 180, 0.62)";
  ctx.lineWidth = 1;
  for (const side of [-1, 1]) {
    ctx.save();
    ctx.scale(1, side);
    ctx.rotate(-0.25 + wing);
    ctx.beginPath();
    ctx.ellipse(-4, -13, 19, 6, -0.12, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
    ctx.restore();
  }

  // Striped abdomen.
  ctx.fillStyle = "rgba(45, 35, 28, 0.96)";
  ctx.beginPath();
  ctx.ellipse(-2, 0, 19, 10, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.save();
  ctx.clip();
  ctx.fillStyle = "rgba(18, 16, 15, 0.8)";
  for (const x of [-12, -5, 2, 9]) ctx.fillRect(x, -11, 3, 22);
  ctx.restore();

  // Thorax and head.
  ctx.fillStyle = "rgba(58, 43, 34, 0.98)";
  ctx.beginPath();
  ctx.ellipse(13, 0, 9, 9, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "rgba(38, 31, 28, 0.98)";
  ctx.beginPath();
  ctx.ellipse(22, 0, 7, 7, 0, 0, Math.PI * 2);
  ctx.fill();

  // Compound eyes and antennae.
  ctx.fillStyle = "rgba(137, 32, 41, 0.95)";
  ctx.beginPath();
  ctx.ellipse(24, -4, 3.5, 3.5, 0, 0, Math.PI * 2);
  ctx.ellipse(24, 4, 3.5, 3.5, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = "rgba(22, 18, 17, 0.8)";
  ctx.lineWidth = 1.2;
  ctx.beginPath();
  ctx.moveTo(26, -3);
  ctx.quadraticCurveTo(34, -9, 36, -7);
  ctx.moveTo(26, 3);
  ctx.quadraticCurveTo(34, 9, 36, 7);
  ctx.stroke();
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
