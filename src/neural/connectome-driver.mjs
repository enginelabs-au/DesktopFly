/**
 * Long-lived Python LIF worker (connectome → motor). No authored neuralWander.
 */

import { spawn } from "node:child_process";
import { createInterface } from "node:readline";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const backendDir = join(repoRoot, "backend");

export function connectomePythonCommand() {
  const uv = process.env.DESKTOPFLY_UV || "uv";
  return { cmd: uv, args: ["run", "python", "-m", "flysim.desktop_neural"], cwd: backendDir };
}

/**
 * @returns {Promise<{
 *   step: (dtS: number, features?: Record<string, number>) => Promise<object>;
 *   status: () => object | null;
 *   shutdown: () => void;
 * }>}
 */
export async function startConnectomeDriver({ timeoutMs = 600000 } = {}) {
  const { cmd, args, cwd } = connectomePythonCommand();
  const child = spawn(cmd, args, {
    cwd,
    stdio: ["pipe", "pipe", "pipe"],
    env: { ...process.env, PYTHONUNBUFFERED: "1" },
  });

  const rl = createInterface({ input: child.stdout });
  let lastTechnical = null;
  let pending = null;
  const queue = [];

  const flush = () => {
    if (pending || queue.length === 0) return;
    pending = queue.shift();
    child.stdin.write(`${pending.line}\n`);
  };

  rl.on("line", (line) => {
    let msg;
    try {
      msg = JSON.parse(line);
    } catch {
      if (pending) pending.reject(new Error(`invalid neural json: ${line}`));
      pending = null;
      flush();
      return;
    }
    if (msg.event === "ready" && msg.technical) {
      lastTechnical = msg.technical;
    }
    if (msg.technical) lastTechnical = msg.technical;
    if (pending) {
      if (msg.ok) pending.resolve(msg);
      else pending.reject(new Error(msg.error || "neural step failed"));
      pending = null;
      flush();
    }
  });

  const ready = new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      reject(new Error("connectome worker ready timeout"));
    }, timeoutMs);
    const onLine = (line) => {
      try {
        const msg = JSON.parse(line);
        if (msg.ok && msg.event === "ready") {
          clearTimeout(timer);
          rl.off("line", onLine);
          lastTechnical = msg.technical;
          resolve(msg);
        } else if (msg.ok === false) {
          clearTimeout(timer);
          reject(new Error(msg.error || "connectome worker failed to start"));
        }
      } catch {
        /* wait for valid ready */
      }
    };
    rl.on("line", onLine);
    child.on("error", (err) => {
      clearTimeout(timer);
      reject(err);
    });
    child.stderr?.on("data", (chunk) => {
      const text = String(chunk);
      if (text.includes("Error") && !pending) {
        /* surfaced on ready reject */
      }
    });
  });

  function request(payload) {
    return new Promise((resolve, reject) => {
      queue.push({
        line: JSON.stringify(payload),
        resolve,
        reject,
      });
      flush();
    });
  }

  await ready;

  return {
    status() {
      return lastTechnical;
    },
    async step(dtS, features = undefined) {
      const msg = await request({
        op: "step",
        dt_s: dtS,
        features,
      });
      if (msg.technical) lastTechnical = msg.technical;
      return msg;
    },
    shutdown() {
      try {
        child.stdin.write(`${JSON.stringify({ op: "shutdown" })}\n`);
      } catch {
        /* closed */
      }
      child.kill();
    },
  };
}

/** One-shot step for unit tests without keeping the child alive. */
export async function connectomeStepOnce(dtS = 0.05) {
  const driver = await startConnectomeDriver();
  try {
    const result = await driver.step(dtS);
    return result;
  } finally {
    driver.shutdown();
  }
}
