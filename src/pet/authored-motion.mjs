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
    surfaceContact: hostRect ? "host-window-surface" : "none",
    transitionSource: "operator",
  };
}

export function detectSurfaceContact({
  pose,
  bounds,
  hostRect = null,
  edgeTolerance = 8,
} = {}) {
  if (!pose || !bounds) return "none";
  const atScreenEdge =
    Math.abs(pose.x - bounds.x) <= edgeTolerance ||
    Math.abs(pose.x - (bounds.x + bounds.width)) <= edgeTolerance ||
    Math.abs(pose.y - bounds.y) <= edgeTolerance ||
    Math.abs(pose.y - (bounds.y + bounds.height)) <= edgeTolerance;
  if (atScreenEdge) return "screen-edge";
  if (hostRect) {
    const insideX = pose.x >= hostRect.x && pose.x <= hostRect.x + hostRect.width;
    const surfaceY = hostRect.y + hostRect.height * 0.12;
    if (insideX && Math.abs(pose.y - surfaceY) <= edgeTolerance * 2) {
      return "host-window-surface";
    }
  }
  return "none";
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
    loomObjectRadiusPoints = 24,
    loomRateRefRadS = 2,
    loomSmoothingS = 0.1,
    takeoffFlightThreshold = 0.5,
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
    this.loomObjectRadiusPoints = loomObjectRadiusPoints;
    this.loomRateRefRadS = loomRateRefRadS;
    this.loomSmoothingS = loomSmoothingS;
    this.takeoffFlightThreshold = takeoffFlightThreshold;
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
      loomObjectRadiusPoints: Number(data.loom_object_radius_points) || 24,
      loomRateRefRadS: Number(data.loom_rate_ref_rad_s) || 2,
      loomSmoothingS: Number(data.loom_smoothing_s) || 0.1,
      takeoffFlightThreshold: Number(data.takeoff_flight_threshold) || 0.5,
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
      surfaceContact: "none",
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
    this._loomPrevTheta = null;
    this._loomRate = 0;
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
    const x = Array.isArray(point) ? point[0] : point?.x;
    const y = Array.isArray(point) ? point[1] : point?.y;
    this._cursor =
      Number.isFinite(Number(x)) && Number.isFinite(Number(y))
        ? [Number(x), Number(y)]
        : null;
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
      } else if (this.pose.surfaceContact === "host-window-surface") {
        // Neutral contact: deterministic walking along the approved host
        // surface. This is geometry, not hunger, reward, or avoidance.
        speed = Math.min(this.config.cursorYieldMaxSpeedPointsS, 18);
        turn = this.config.wanderTurnRadS * 0.5;
        locomotion = "crawl";
        source = "neutral-contact";
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
    this.pose.surfaceContact = detectSurfaceContact({
      pose: this.pose,
      bounds: this.bounds,
      hostRect: this._hostRect,
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

  /**
   * What the fly's two eyes see of the cursor, as plain numbers. The cursor is
   * treated as a fixed-size object; its visual angle and how fast that angle
   * grows (looming) is measured, smoothed briefly, and split between the left
   * and right eye by bearing. Eyes cover about 150 degrees to each side with a
   * small binocular overlap, and there is a blind zone behind. This only
   * describes the stimulus; the network alone decides any response. The same
   * signal goes to every looming-detector neuron on that side (no per-neuron
   * retinotopy is available in the data).
   */
  loomFeatures(dtS) {
    const none = { loom_left: 0, loom_right: 0 };
    if (!this._cursor || !(dtS > 0)) {
      this._loomPrevTheta = null;
      this._loomRate = 0;
      return none;
    }
    const cfg = this.config;
    const dx = this._cursor[0] - this.pose.x;
    const dy = this._cursor[1] - this.pose.y;
    const dist = Math.max(Math.hypot(dx, dy), 1e-3);
    const theta = 2 * Math.atan(cfg.loomObjectRadiusPoints / dist);
    const rate = this._loomPrevTheta == null ? 0 : (theta - this._loomPrevTheta) / dtS;
    this._loomPrevTheta = theta;
    this._loomRate += (1 - Math.exp(-dtS / cfg.loomSmoothingS)) * (rate - this._loomRate);
    // Only expansion counts as looming.
    const strength = Math.min(1, Math.max(0, this._loomRate / cfg.loomRateRefRadS));
    const bearing = wrapHeading(Math.atan2(dy, dx) - this.pose.headingRad); // + = right
    const deg = (bearing * 180) / Math.PI;
    const clamp01 = (v) => Math.min(1, Math.max(0, v));
    const left = deg >= -150 ? clamp01((20 - deg) / 40) : 0;
    const right = deg <= 150 ? clamp01((deg + 20) / 40) : 0;
    return { loom_left: strength * left, loom_right: strength * right };
  }

  /**
   * Connectome-driven motion. Speed and turn come straight from the network
   * readout. The only code bounds are the speed ceiling and the screen clamp.
   * No shaping, steering, flee, or edge rule is applied here.
   */
  _applyConnectomeMotor(dtS, motor, transitionSource = "connectome") {
    const cfg = this.config;
    const speed = Math.min(cfg.maxSpeedPointsS, Math.max(0, Number(motor?.speed) || 0));
    const turn = Number(motor?.turn) || 0;
    this.pose = integratePose(this.pose, {
      dtS,
      speedPointsS: speed,
      turnRateRadS: turn,
      bounds: this.bounds,
      // Label only (drives wing display): takeoff is the giant-fiber readout.
      locomotion:
        Number(motor?.takeoff) >= cfg.takeoffFlightThreshold
          ? "flight"
          : speed > 0.2
            ? "crawl"
            : "idle",
      depth01: this.pose.depth01,
      transitionSource,
    });
    this.pose.surfaceContact = detectSurfaceContact({
      pose: this.pose,
      bounds: this.bounds,
      hostRect: this._hostRect,
    });
    this.pose.hostSurfaceId = this._hostRect ? "host-window" : null;
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
    if (now >= this._yieldUntilS && now < this._yieldCooldownUntilS) {
      return { vx: 0, vy: 0 };
    }
    if (now >= this._yieldUntilS) {
      this._yieldUntilS = now + cfg.cursorYieldDurationS;
      this._yieldCooldownUntilS = this._yieldUntilS + cfg.cursorYieldCooldownS;
    }
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
  connectomeDriver = null,
} = {}) {
  const useAuthoredWander = controllerKind === "lif" && !connectomeDriver;
  const motion = new AuthoredAnimationController({
    clock: new PresentationClock({ now }),
    config: AuthoredMotionConfig.fromDesktopPet(petConfig),
    bounds: bounds || { x: 0, y: 0, width: 1440, height: 900 },
    mode,
    neuralWander: useAuthoredWander,
  });

  let lastConnectomeMotor = null;

  return {
    async step({ neuralFeatures = {}, screenFeatures = null } = {}) {
      if (connectomeDriver) {
        const dt = motion.clock.advance();
        motion._accumulatorS += dt;
        const block = motion.config.physicsDtS;
        const blocks = Math.floor(motion._accumulatorS / block + 1e-9);
        if (blocks <= 0) return motion.pose;
        motion._accumulatorS -= blocks * block;
        // What the eyes see of the cursor, plus any opt-in screen features; numbers only.
        const features = { ...neuralFeatures, ...motion.loomFeatures(dt) };
        try {
          let motors = [];
          let source = "connectome";
          if (typeof connectomeDriver.stepBlocks === "function") {
            // One request per tick; the worker times every block separately.
            const msg = await connectomeDriver.stepBlocks(block, blocks, features);
            motors =
              Array.isArray(msg.motors) && msg.motors.length ? msg.motors : [msg.motor];
            source = msg.transition_source || source;
          } else {
            for (let i = 0; i < blocks; i += 1) {
              const msg = await connectomeDriver.step(block, features);
              motors.push(msg.motor);
              source = msg.transition_source || source;
            }
          }
          for (const m of motors) {
            lastConnectomeMotor = m;
            motion._applyConnectomeMotor(block, m, source);
          }
        } catch {
          lastConnectomeMotor = null;
          motion.pose = {
            ...motion.pose,
            speedPointsS: 0,
            locomotion: "idle",
            transitionSource: "connectome-error",
          };
        }
        return motion.pose;
      }
      motion._screenFeatures = screenFeatures;
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
    setCursor(point, options) {
      motion.setCursor(point, options);
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
    getConnectomeTechnical() {
      return connectomeDriver?.status?.() ?? null;
    },
    getLastConnectomeMotor() {
      return lastConnectomeMotor;
    },
  };
}
