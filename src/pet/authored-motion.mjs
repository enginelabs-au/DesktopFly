/**
 * Portable authored-motion + LIF presentation tick for the desktop pet.
 * Presentation only — not neural evidence. Drives pose for Electron phase 3.
 */

export function scaleForDepth(depth01) {
  if (!Number.isFinite(depth01) || depth01 < 0 || depth01 > 1) {
    throw new Error("invalid depth01");
  }
  return 1 - 0.35 * depth01;
}

export function easeSmoothstep(t) {
  const x = Math.min(Math.max(t, 0), 1);
  return x * x * (3 - 2 * x);
}

export function wrapHeading(headingRad) {
  return ((headingRad + Math.PI) % (2 * Math.PI)) - Math.PI;
}

export function clampCursorYieldSpeed(vx, vy, maxSpeed) {
  const speed = Math.hypot(vx, vy);
  if (speed <= maxSpeed || speed === 0) return { vx, vy, speed };
  const scale = maxSpeed / speed;
  return { vx: vx * scale, vy: vy * scale, speed: maxSpeed };
}

/** Find-fly placement without a neural worker. */
export function findFlyPose({ hostRect, bounds, headingRad = 0 }) {
  let x;
  let y;
  let hostSurfaceId = null;
  if (hostRect) {
    x = hostRect.x + hostRect.width * 0.5;
    y = hostRect.y + hostRect.height * 0.15;
    hostSurfaceId = "host-window";
  } else {
    x = bounds.x + bounds.width * 0.5;
    y = bounds.y + bounds.height * 0.5;
  }
  x = Math.min(Math.max(x, bounds.x), bounds.x + bounds.width);
  y = Math.min(Math.max(y, bounds.y), bounds.y + bounds.height);
  return {
    x,
    y,
    headingRad,
    speedPointsS: 0,
    depth01: 0,
    locomotion: "idle",
    visible: true,
    hostSurfaceId,
    transitionSource: "operator",
  };
}

export class PresentationClock {
  constructor({ maxCatchUpS = 0.05, now = () => Date.now() } = {}) {
    this.maxCatchUpS = maxCatchUpS;
    this.now = now;
    this.simTimeS = 0;
    this._lastWallS = null;
    this._stopped = false;
  }

  advance() {
    if (this._stopped) return 0;
    const wallS = this.now() / 1000;
    if (this._lastWallS == null) {
      this._lastWallS = wallS;
      return 0;
    }
    let dt = wallS - this._lastWallS;
    this._lastWallS = wallS;
    if (dt < 0) dt = 0;
    if (dt > this.maxCatchUpS) dt = this.maxCatchUpS;
    this.simTimeS += dt;
    return dt;
  }

  /** Test hook — advance simulated time without a live wall clock. */
  advanceFakeWall(deltaS) {
    if (this._stopped) return 0;
    if (this._lastWallS == null) this._lastWallS = 0;
    let dt = Math.max(0, Number(deltaS) || 0);
    if (dt > this.maxCatchUpS) dt = this.maxCatchUpS;
    this._lastWallS += dt;
    this.simTimeS += dt;
    return dt;
  }

  setFakeWallS(wallS) {
    this._lastWallS = wallS;
  }

  stop() {
    this._stopped = true;
  }
}

export function clampPoint(bounds, x, y) {
  return {
    x: Math.min(Math.max(x, bounds.x), bounds.x + bounds.width),
    y: Math.min(Math.max(y, bounds.y), bounds.y + bounds.height),
  };
}

export function integratePose(
  pose,
  { dtS, speedPointsS, turnRateRadS, bounds, locomotion, depth01, transitionSource },
) {
  if (dtS < 0 || !Number.isFinite(dtS)) throw new Error("invalid dt");
  const speed = Math.max(0, Number(speedPointsS));
  const heading = wrapHeading(pose.headingRad + turnRateRadS * dtS);
  let x = pose.x + Math.cos(heading) * speed * dtS;
  let y = pose.y + Math.sin(heading) * speed * dtS;
  ({ x, y } = clampPoint(bounds, x, y));
  return {
    ...pose,
    x,
    y,
    headingRad: heading,
    speedPointsS: speed,
    depth01: depth01 == null ? pose.depth01 : depth01,
    locomotion: locomotion == null ? pose.locomotion : locomotion,
    transitionSource: transitionSource || pose.transitionSource,
  };
}

export class AuthoredMotionConfig {
  constructor({
    physicsDtS = 0.005,
    cruiseSpeedPointsS = 80,
    maxSpeedPointsS = 160,
    wanderTurnRadS = 0.35,
    cursorYieldRadiusPoints = 40,
    cursorYieldMaxSpeedPointsS = 40,
    cursorYieldDurationS = 0.25,
    cursorYieldCooldownS = 0.75,
    depthTransitionS = 0.8,
    wingBeatHz = 8,
  } = {}) {
    this.physicsDtS = physicsDtS;
    this.cruiseSpeedPointsS = cruiseSpeedPointsS;
    this.maxSpeedPointsS = maxSpeedPointsS;
    this.wanderTurnRadS = wanderTurnRadS;
    this.cursorYieldRadiusPoints = cursorYieldRadiusPoints;
    this.cursorYieldMaxSpeedPointsS = cursorYieldMaxSpeedPointsS;
    this.cursorYieldDurationS = cursorYieldDurationS;
    this.cursorYieldCooldownS = cursorYieldCooldownS;
    this.depthTransitionS = depthTransitionS;
    this.wingBeatHz = wingBeatHz;
  }

  static fromDesktopPet(data = {}) {
    return new AuthoredMotionConfig({
      cruiseSpeedPointsS: Number(data.cruise_speed_points_s) || 80,
      maxSpeedPointsS: Number(data.max_speed_points_s) || 160,
      cursorYieldRadiusPoints: Number(data.cursor_yield_radius_points) || 40,
      cursorYieldMaxSpeedPointsS: Number(data.cursor_yield_max_speed_points_s) || 40,
      cursorYieldDurationS: (Number(data.cursor_yield_duration_ms) || 250) / 1000,
      cursorYieldCooldownS: (Number(data.cursor_yield_cooldown_ms) || 750) / 1000,
      depthTransitionS: (Number(data.depth_transition_ms) || 800) / 1000,
      wingBeatHz: Number(data.wing_beat_hz) || 8,
    });
  }
}

/**
 * Deterministic presentation controller. When neuralWander is true (LIF policy on),
 * idle open-space motion is obvious on screen.
 */
export class AuthoredAnimationController {
  constructor({
    clock = new PresentationClock(),
    config = new AuthoredMotionConfig(),
    bounds = { x: 0, y: 0, width: 1440, height: 900 },
    mode = "follow_my_window",
    neuralWander = false,
  } = {}) {
    this.clock = clock;
    this.config = config;
    this.bounds = bounds;
    this.mode = mode;
    this.neuralWander = neuralWander;
    this.pose = {
      x: bounds.x + bounds.width * 0.5,
      y: bounds.y + bounds.height * 0.5,
      headingRad: 0,
      speedPointsS: 0,
      depth01: 0,
      locomotion: "idle",
      visible: true,
      hostSurfaceId: null,
      transitionSource: "authored",
    };
    this._hostRect = null;
    this._cursor = null;
    this._cursorMoving = false;
    this._yieldUntilS = -1;
    this._yieldCooldownUntilS = -1;
    this._depthFrom = 0;
    this._depthTo = 0;
    this._depthT0 = 0;
    this._depthActive = false;
    this._hidden = false;
    this._accumulatorS = 0;
  }

  setBounds(bounds) {
    this.bounds = bounds;
  }

  setMode(mode) {
    this.mode = mode;
  }

  setHostWindow(rect) {
    this._hostRect = rect;
  }

  setCursor(point, { moving = false } = {}) {
    this._cursor = point;
    this._cursorMoving = moving;
  }

  findFly() {
    this._hidden = false;
    this._depthActive = false;
    const headingRad = this.pose.headingRad;
    this.pose = findFlyPose({
      hostRect: this._hostRect
        ? {
            x: this._hostRect.x,
            y: this._hostRect.y,
            width: this._hostRect.width,
            height: this._hostRect.height,
          }
        : null,
      bounds: this.bounds,
      headingRad,
    });
    return this.pose;
  }

  beginHideFlight() {
    if (this.mode !== "explore_and_hide") return;
    this._hidden = true;
    this._depthFrom = this.pose.depth01;
    this._depthTo = 1;
    this._depthT0 = this.clock.simTimeS;
    this._depthActive = true;
  }

  wingPhase() {
    return (this.clock.simTimeS * this.config.wingBeatHz) % 1;
  }

  step() {
    const dt = this.clock.advance();
    this._accumulatorS += dt;
    while (this._accumulatorS >= this.config.physicsDtS) {
      this._integrate(this.config.physicsDtS);
      this._accumulatorS -= this.config.physicsDtS;
    }
    return this.pose;
  }

  _wanderTurn() {
    const t = this.clock.simTimeS;
    return this.config.wanderTurnRadS * (Math.sin(t * 1.1) + 0.45 * Math.cos(t * 2.3));
  }

  _integrate(dtS) {
    let speed = 0;
    let turn = 0;
    let locomotion = this.pose.locomotion;
    let source = "authored";

    if (this._hidden && this.mode === "explore_and_hide") {
      locomotion = "flight";
      speed = this.config.cruiseSpeedPointsS * 0.5;
      turn = this.config.wanderTurnRadS;
    } else if (this.mode === "follow_my_window" && this._hostRect) {
      const tx = this._hostRect.x + this._hostRect.width * 0.5;
      const ty = this._hostRect.y + this._hostRect.height * 0.12;
      const dx = tx - this.pose.x;
      const dy = ty - this.pose.y;
      const dist = Math.hypot(dx, dy);
      if (dist > 4) {
        const desired = Math.atan2(dy, dx);
        const err = wrapHeading(desired - this.pose.headingRad);
        turn = Math.max(-2, Math.min(2, err / Math.max(dtS, 1e-6)));
        speed = Math.min(this.config.cruiseSpeedPointsS, dist * 2);
        locomotion = this.pose.depth01 < 0.15 ? "crawl" : "flight";
        source = "geometry";
      } else if (this.neuralWander) {
        locomotion = "flight";
        speed = this.config.cruiseSpeedPointsS * 0.55;
        turn = this._wanderTurn();
      } else {
        locomotion = "idle";
        speed = 0;
      }
    } else if (this.neuralWander && !this._hidden) {
      locomotion = "flight";
      speed = this.config.cruiseSpeedPointsS * 0.65;
      turn = this._wanderTurn();
      source = "authored";
    } else {
      locomotion = this.pose.speedPointsS < 1 ? "idle" : "flight";
      speed = 0;
    }

    const yieldVel = this._cursorYieldVelocity();
    if (yieldVel.vx || yieldVel.vy) {
      source = "geometry";
      const baseVx = Math.cos(this.pose.headingRad) * speed;
      const baseVy = Math.sin(this.pose.headingRad) * speed;
      const vx = baseVx + yieldVel.vx;
      const vy = baseVy + yieldVel.vy;
      speed = Math.min(this.config.maxSpeedPointsS, Math.hypot(vx, vy));
      if (speed > 0) {
        turn =
          wrapHeading(Math.atan2(vy, vx) - this.pose.headingRad) / Math.max(dtS, 1e-6);
      }
    }

    const depth = this._updateDepth();
    const hostSurfaceId = this._hostRect ? "host-window" : null;
    this.pose = integratePose(this.pose, {
      dtS,
      speedPointsS: speed,
      turnRateRadS: turn,
      bounds: this.bounds,
      locomotion,
      depth01: depth,
      transitionSource: source,
    });
    this.pose.hostSurfaceId = hostSurfaceId;

    if (this._hidden && depth >= 0.99) {
      this.pose = {
        ...this.pose,
        speedPointsS: 0,
        depth01: 1,
        locomotion: "idle",
        visible: false,
        transitionSource: "operator",
      };
    }
  }

  _updateDepth() {
    if (!this._depthActive) return this.pose.depth01;
    const dur = Math.min(1.2, Math.max(0.4, this.config.depthTransitionS));
    const t = (this.clock.simTimeS - this._depthT0) / dur;
    if (t >= 1) {
      this._depthActive = false;
      return this._depthTo;
    }
    return this._depthFrom + (this._depthTo - this._depthFrom) * easeSmoothstep(t);
  }

  _cursorYieldVelocity() {
    const cfg = this.config;
    const now = this.clock.simTimeS;
    if (!this._cursor || !this._cursorMoving) return { vx: 0, vy: 0 };
    const [cx, cy] = this._cursor;
    const dx = this.pose.x - cx;
    const dy = this.pose.y - cy;
    const dist = Math.hypot(dx, dy);
    if (dist > cfg.cursorYieldRadiusPoints || dist === 0) return { vx: 0, vy: 0 };
    if (now < this._yieldCooldownUntilS) return { vx: 0, vy: 0 };
    if (now > this._yieldUntilS) {
      this._yieldUntilS = now + cfg.cursorYieldDurationS;
      this._yieldCooldownUntilS = this._yieldUntilS + cfg.cursorYieldCooldownS;
    }
    if (now > this._yieldUntilS) return { vx: 0, vy: 0 };
    const nx = dx / dist;
    const ny = dy / dist;
    const tx = -ny;
    const ty = nx;
    let vx = (tx * 0.35 + nx) * cfg.cursorYieldMaxSpeedPointsS;
    let vy = (ty * 0.35 + ny) * cfg.cursorYieldMaxSpeedPointsS;
    const capped = clampCursorYieldSpeed(vx, vy, cfg.cursorYieldMaxSpeedPointsS);
    return { vx: capped.vx, vy: capped.vy };
  }
}

export function createPetMotionController({
  petConfig,
  controllerKind = "authored-animation",
  bounds,
  mode = "follow_my_window",
  now = () => Date.now(),
} = {}) {
  const motion = new AuthoredAnimationController({
    clock: new PresentationClock({ now }),
    config: AuthoredMotionConfig.fromDesktopPet(petConfig),
    bounds: bounds || { x: 0, y: 0, width: 1440, height: 900 },
    mode,
    neuralWander: controllerKind === "lif",
  });

  return {
    step() {
      return motion.step();
    },
    findFly() {
      return motion.findFly();
    },
    beginHideFlight() {
      motion.beginHideFlight();
    },
    setBounds(nextBounds) {
      motion.setBounds(nextBounds);
    },
    setMode(nextMode) {
      motion.setMode(nextMode);
      if (nextMode === "explore_and_hide") motion.beginHideFlight();
    },
    syncFocusSnapshot(focusSnap) {
      const host = focusSnap?.host;
      if (host?.rect) {
        motion.setHostWindow({
          x: host.rect.x,
          y: host.rect.y,
          width: host.rect.width,
          height: host.rect.height,
        });
      } else {
        motion.setHostWindow(null);
      }
    },
    getPose() {
      return motion.pose;
    },
    wingPhase() {
      return motion.wingPhase();
    },
  };
}
