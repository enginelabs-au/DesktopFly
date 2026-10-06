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
  let faulted = false;
  let faultReason = null;

  const flush = () => {
    if (faulted || pending || queue.length === 0) return;
    pending = queue.shift();
    child.stdin.write(`${pending.line}\n`);
  };

  const rejectQueued = (error) => {
    if (pending) {
      pending.reject(error);
      pending = null;
    }
    while (queue.length) {
      queue.shift().reject(error);
    }
  };

  rl.on("line", (line) => {
    let msg;
    try {
      msg = JSON.parse(line);
    } catch {
      faulted = true;
      faultReason = `invalid neural json: ${line}`;
      rejectQueued(new Error(faultReason));
      return;
    }
    if (msg.event === "ready" && msg.technical) {
      lastTechnical = msg.technical;
    }
    if (msg.technical) lastTechnical = msg.technical;
    if (pending) {
      if (msg.ok) pending.resolve(msg);
      else {
        faulted = true;
        faultReason = msg.error || "neural step failed";
        rejectQueued(new Error(faultReason));
      }
      if (!faulted) {
        pending = null;
        flush();
      }
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
      return {
        ...(lastTechnical || {}),
        faulted,
        faultReason,
      };
    },
    async step(dtS, features = undefined) {
      if (faulted) {
        throw new Error(faultReason || "connectome worker is permanently stopped");
      }
      const msg = await request({
        op: "step",
        dt_s: dtS,
        features,
      });
      if (msg.technical) lastTechnical = msg.technical;
      return msg;
    },
    shutdown() {
      faulted = true;
      faultReason = faultReason || "operator_stop";
      rejectQueued(new Error(faultReason));
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
