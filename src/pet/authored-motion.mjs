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
    eyeObjectRadiusPoints = 24,
    retinaH1Max = 36,
    retinaH2Max = 39,
    retinaFarPoints = 900,
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
    this.eyeObjectRadiusPoints = eyeObjectRadiusPoints;
    this.retinaH1Max = retinaH1Max;
    this.retinaH2Max = retinaH2Max;
    this.retinaFarPoints = retinaFarPoints;
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
      eyeObjectRadiusPoints: Number(data.eye_object_radius_points) || 24,
      retinaH1Max: Number(data.retina_h1_max) || 36,
      retinaH2Max: Number(data.retina_h2_max) || 39,
      retinaFarPoints: Number(data.retina_far_points) || 900,
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
    random = Math.random,
  } = {}) {
    this.clock = clock;
    this.config = config;
    this.bounds = bounds;
    this.mode = mode;
    this.neuralWander = neuralWander;
    this._random = random;
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
    this._retinaPlane = null;
    this._cursorMoving = false;
    this._yieldUntilS = -1;
    this._yieldCooldownUntilS = -1;
    this._depthFrom = 0;
    this._depthTo = 0;
    this._depthT0 = 0;
    this._depthActive = false;
    this._hidden = false;
    this._accumulatorS = 0;
    this._cursorDist = null;
    this._bout = null;
    this._boutUntil = 0;
    this._boutSpeed = 60;
    this._boutBias = 0;
    this._turnHeading = 0;
    this._launchHeading = 0;
    this._flyCurve = 0;
    this._flyDepth = 0.8;
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

  setRetinaPlane(plane) {
    this._retinaPlane =
      plane && Array.isArray(plane.samples) && plane.width > 0 && plane.height > 0
        ? plane
        : null;
  }

  /**
   * Cursor image for the connectome. hex1 is bearing within an eye, hex2 is
   * distance. Eyes cover about 150 degrees with a blind zone behind. The
   * screen thumbnail is not sent here: a full grid drives the live slice over
   * the 4 ms budget and stops the worker. The body reads that thumbnail
   * itself in _view.
   */
  retinaFeatures() {
    const cfg = this.config;
    const h1Max = cfg.retinaH1Max;
    const h2Max = cfg.retinaH2Max;
    const out = {};
    const put = (side, h1, h2, value) => {
      if (h1 < 1 || h2 < 1 || h1 > h1Max || h2 > h2Max || !(value > 0)) return;
      const key = `hex_${side}_${h1}_${h2}`;
      out[key] = Math.min(1, Math.max(out[key] || 0, value));
    };
    const eyes = [
      ["L", -150, 20],
      ["R", -20, 150],
    ];
    if (this._cursor) {
      const dx = this._cursor[0] - this.pose.x;
      const dy = this._cursor[1] - this.pose.y;
      const dist = Math.max(Math.hypot(dx, dy), 1);
      const deg = (wrapHeading(Math.atan2(dy, dx) - this.pose.headingRad) * 180) / Math.PI;
      const h2 =
        1 +
        Math.round((Math.min(dist, cfg.retinaFarPoints) / cfg.retinaFarPoints) * (h2Max - 1));
      const size = Math.min(1, (2 * Math.atan(cfg.eyeObjectRadiusPoints / dist)) / Math.PI);
      for (const [side, lo, hi] of eyes) {
        if (deg < lo || deg > hi) continue;
        const h1 = 1 + Math.round(((deg - lo) / (hi - lo)) * (h1Max - 1));
        for (let a = -1; a <= 1; a += 1) {
          for (let b = -1; b <= 1; b += 1) {
            put(side, h1 + a, h2 + b, a === 0 && b === 0 ? Math.max(size, 0.5) : size * 0.5);
          }
        }
      }
    }
    return out;
  }

  /**
   * Bout model of a fly on a surface. Each walk, turn, stop, groom, and flight
   * draws its own length from a heavy-tailed distribution when the bout
   * starts, then runs lawfully until that length is up or a stimulus cuts it
   * short. A looming cursor starts a flight whose duration is not reused.
   * Contrast in the thumbnail biases turns. This is not a clock and not a
   * sentience claim.
   */
  _applyFlyBody(dtS) {
    const cfg = this.config;
    const dt = Math.max(dtS, 1e-3);
    let desired = null;
    let speed = 0;
    let locomotion = "idle";
    let takeoff = 0;
    let groom = 0;
    let source = "geometry";

    const now = this.clock.simTimeS;
    const cursor = this._cursor;
    let cursorDist = null;
    if (cursor) {
      cursorDist = Math.hypot(this.pose.x - cursor[0], this.pose.y - cursor[1]);
    }
    const closing =
      cursorDist != null &&
      this._cursorDist != null &&
      this._cursorDist - cursorDist > 6;
    const launchReach = cfg.cursorYieldRadiusPoints;
    const cursorTriggers =
      cursorDist != null &&
      cursorDist > 0 &&
      (cursorDist < launchReach || (closing && cursorDist < launchReach * 1.6));
    if (cursorDist != null) this._cursorDist = cursorDist;
    if (!this._bout) this._enterBout(cursorTriggers ? "fly" : "walk", now, cursor);
    if (cursorTriggers && this._bout !== "fly" && this._bout !== "land") {
      this._enterBout("fly", now, cursor);
    }
    if (now >= this._boutUntil) this._finishBout(now, cursor);

    const view = this._view();
    if (this._bout === "fly" && view.openAhead < 90 && now - this._boutT0 > 0.45) {
      this._enterBout("land", now, cursor);
    }
    let depthTarget = 0;
    let turnLimit = 2.5;
    if (this._bout === "fly") {
      if (cursor && cursorDist != null && cursorDist < launchReach) {
        const away = this._escapeHeading(cursor);
        this._launchHeading += wrapHeading(away - this._launchHeading) * Math.min(1, dtS * 1.5);
      }
      this._launchHeading += this._flyCurve * dtS;
      desired = this._launchHeading;
      speed = this._boutSpeed;
      locomotion = "flight";
      takeoff = 1;
      depthTarget = this._flyDepth;
      turnLimit = 6;
    } else if (this._bout === "land") {
      desired = this.pose.headingRad;
      speed = this._boutSpeed * 0.25;
      locomotion = "flight";
      takeoff = 0.35;
      depthTarget = 0;
      turnLimit = 2;
    } else if (this._bout === "groom" || this._bout === "stop") {
      desired = this.pose.headingRad;
      speed = 0;
      locomotion = "idle";
      groom = this._bout === "groom" ? 1 : 0;
    } else if (this._bout === "saccade") {
      desired = this._turnHeading;
      speed = Math.min(cfg.cruiseSpeedPointsS * 0.3, this._boutSpeed);
      locomotion = "crawl";
      turnLimit = 16;
    } else {
      if (view.nearScore > 0.18 && view.nearScore + 0.02 >= view.bestScore) {
        this._enterBout("groom", now, cursor);
        desired = this.pose.headingRad;
        speed = 0;
        locomotion = "idle";
        groom = 1;
      } else {
        if (view.openAhead < 48) this._finishBout(now, cursor);
        desired =
          view.bestScore > 0.08 ? this.pose.headingRad + view.bestBearing : this._boutHeading;
        speed = this._boutSpeed;
        locomotion = "crawl";
      }
    }

    const depth = this.pose.depth01 + (depthTarget - this.pose.depth01) * Math.min(1, dtS / 0.12);
    const err = wrapHeading((desired ?? this.pose.headingRad) - this.pose.headingRad);
    const turn = Math.max(-turnLimit, Math.min(turnLimit, err / dt));
    const speedCap = this._bout === "fly" ? 560 : cfg.maxSpeedPointsS;
    this.pose = integratePose(this.pose, {
      dtS,
      speedPointsS: Math.min(speed, speedCap),
      turnRateRadS: turn,
      bounds: this.bounds,
      locomotion,
      depth01: depth,
      transitionSource: source,
    });
    this.pose.takeoff = takeoff;
    this.pose.groom = groom;
    this.pose.bout = this._bout;
    this.pose.boutS = this._boutSpan;
    this.pose.surfaceContact = detectSurfaceContact({
      pose: this.pose,
      bounds: this.bounds,
      hostRect: this._hostRect,
    });
    this.pose.hostSurfaceId = this._hostRect ? "host-window" : null;
  }

  _unit() {
    const x = Number(this._random());
    if (!Number.isFinite(x)) return 0.5;
    return Math.min(0.999999, Math.max(0.000001, x));
  }

  _logNormal(median, sigma) {
    const u = this._unit();
    const v = this._unit();
    const z = Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
    return median * Math.exp(sigma * z);
  }

  _enterBout(name, now, cursor) {
    const clamp = (value, lo, hi) => Math.min(hi, Math.max(lo, value));
    this._bout = name;
    this._boutT0 = now;
    let span = 0.5;
    if (name === "walk") {
      span = clamp(this._logNormal(1.2, 0.75), 0.4, 8);
      this._boutSpeed = clamp(this._logNormal(58, 0.4), 28, 120);
      this._boutHeading = this.pose.headingRad + (this._unit() - 0.5) * 0.4;
    } else if (name === "saccade") {
      span = clamp(this._logNormal(0.11, 0.35), 0.06, 0.28);
      const view = this._view();
      const toward =
        view.bestScore > 0.08 ? view.bestBearing : this._openSideSign() * (0.6 + this._unit());
      this._turnHeading = this.pose.headingRad + toward + (this._unit() - 0.5) * 1.2;
      this._boutSpeed = 30;
    } else if (name === "stop") {
      span = clamp(this._logNormal(0.7, 0.6), 0.2, 3);
    } else if (name === "groom") {
      span = clamp(this._logNormal(1.6, 0.6), 0.6, 6);
    } else if (name === "fly") {
      span = clamp(this._logNormal(2.4, 0.9), 0.6, 20);
      this._boutSpeed = clamp(this._logNormal(400, 0.28), 240, 540);
      this._launchHeading = cursor
        ? this._escapeHeading(cursor)
        : this.pose.headingRad + (this._unit() - 0.5);
      this._flyCurve = (this._unit() - 0.5) * 1.1;
      this._flyDepth = clamp(0.55 + this._unit() * 0.4, 0.55, 0.95);
    } else if (name === "land") {
      span = clamp(this._logNormal(0.45, 0.4), 0.2, 1.2);
    }
    this._boutSpan = span;
    this._boutUntil = now + span;
  }

  _finishBout(now, cursor) {
    const u = this._unit();
    if (this._bout === "walk") this._enterBout(u < 0.4 ? "stop" : "saccade", now, cursor);
    else if (this._bout === "saccade") this._enterBout(u < 0.3 ? "stop" : "walk", now, cursor);
    else if (this._bout === "stop") this._enterBout(u < 0.72 ? "groom" : "walk", now, cursor);
    else if (this._bout === "groom") this._enterBout("walk", now, cursor);
    else if (this._bout === "fly") this._enterBout("land", now, cursor);
    else if (this._bout === "land") this._enterBout(u < 0.8 ? "groom" : "walk", now, cursor);
    else this._enterBout("walk", now, cursor);
  }

  /** Direction away from the cursor that still stays on the screen. */
  _escapeHeading(cursor) {
    const away = Math.atan2(this.pose.y - cursor[1], this.pose.x - cursor[0]);
    const b = this.bounds;
    const inside = (heading) => {
      const x = this.pose.x + Math.cos(heading) * 120;
      const y = this.pose.y + Math.sin(heading) * 120;
      return (
        x > b.x + 36 &&
        y > b.y + 36 &&
        x < b.x + b.width - 36 &&
        y < b.y + b.height - 36
      );
    };
    if (inside(away)) return away;
    let best = away;
    let bestDist = -1;
    for (const extra of [Math.PI / 2, -Math.PI / 2, (3 * Math.PI) / 4, (-3 * Math.PI) / 4, Math.PI]) {
      const heading = away + extra;
      if (!inside(heading)) continue;
      const x = this.pose.x + Math.cos(heading) * 120;
      const y = this.pose.y + Math.sin(heading) * 120;
      const dist = Math.hypot(x - cursor[0], y - cursor[1]);
      if (dist > bestDist) {
        bestDist = dist;
        best = heading;
      }
    }
    return best;
  }

  /**
   * What is in front of the fly. Bearings are relative to heading.
   * Near samples are the ones a fly would stop and inspect.
   */
  _view() {
    const samples = [];
    const bearings = [-0.9, -0.45, 0, 0.45, 0.9];
    const distances = [90, 200, 380];
    for (const bearing of bearings) {
      for (const dist of distances) {
        const rad = this.pose.headingRad + bearing;
        const luma = this._lumaAt(
          this.pose.x + Math.cos(rad) * dist,
          this.pose.y + Math.sin(rad) * dist,
        );
        if (luma == null) continue;
        samples.push({ bearing, dist, luma });
      }
    }
    const openAhead = this._clearance(this.pose.headingRad);
    const left = this._clearance(this.pose.headingRad - Math.PI / 2);
    const right = this._clearance(this.pose.headingRad + Math.PI / 2);
    const empty = {
      bestBearing: 0,
      bestScore: 0,
      bestDist: 999,
      nearScore: 0,
      openAhead,
      openSideBias: Math.abs(left - right) / Math.max(left + right, 1),
    };
    if (samples.length < 3) return empty;
    const mean = samples.reduce((sum, row) => sum + row.luma, 0) / samples.length;
    let best = empty;
    let nearScore = 0;
    for (const row of samples) {
      const score = Math.abs(row.luma - mean);
      if (row.dist === 90) nearScore = Math.max(nearScore, score);
      if (score > best.bestScore) {
        best = {
          ...empty,
          bestBearing: row.bearing,
          bestScore: score,
          bestDist: row.dist,
          nearScore,
        };
      }
    }
    best.nearScore = nearScore;
    return best;
  }

  _clearance(heading) {
    const b = this.bounds;
    const dx = Math.cos(heading);
    const dy = Math.sin(heading);
    let limit = 4000;
    if (dx > 0.01) limit = Math.min(limit, (b.x + b.width - this.pose.x) / dx);
    if (dx < -0.01) limit = Math.min(limit, (b.x - this.pose.x) / dx);
    if (dy > 0.01) limit = Math.min(limit, (b.y + b.height - this.pose.y) / dy);
    if (dy < -0.01) limit = Math.min(limit, (b.y - this.pose.y) / dy);
    return Math.max(0, limit);
  }

  _openSideSign() {
    const left = this._clearance(this.pose.headingRad - Math.PI / 2);
    const right = this._clearance(this.pose.headingRad + Math.PI / 2);
    if (Math.abs(left - right) < 8) return this.pose.x < this.bounds.x + this.bounds.width / 2 ? 1 : -1;
    return left > right ? -1 : 1;
  }

  _lumaAt(x, y) {
    const plane = this._retinaPlane;
    if (!plane || !(plane.width > 0) || !(plane.height > 0)) return null;
    const b = this.bounds;
    const u = (x - b.x) / b.width;
    const v = (y - b.y) / b.height;
    if (u < 0 || v < 0 || u > 1 || v > 1) return null;
    const px = Math.min(plane.width - 1, Math.max(0, Math.floor(u * plane.width)));
    const py = Math.min(plane.height - 1, Math.max(0, Math.floor(v * plane.height)));
    const value = plane.samples[py * plane.width + px];
    return Number.isFinite(value) ? value : null;
  }

  /**
   * Kept so a connectome motor can still be applied in tests of the readout
   * path. The live pet does not use it; see _applyFlyBody.
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
      locomotion: speed > 0.2 ? "crawl" : "idle",
      depth01: this.pose.depth01,
      transitionSource,
    });
    this.pose.takeoff = Math.min(1, Math.max(0, Number(motor?.takeoff) || 0));
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
  random = Math.random,
} = {}) {
  const useAuthoredWander = controllerKind === "lif" && !connectomeDriver;
  const motion = new AuthoredAnimationController({
    clock: new PresentationClock({ now }),
    config: AuthoredMotionConfig.fromDesktopPet(petConfig),
    bounds: bounds || { x: 0, y: 0, width: 1440, height: 900 },
    mode,
    neuralWander: useAuthoredWander,
    random,
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
        const features = { ...neuralFeatures, ...motion.retinaFeatures() };
        try {
          let motors = [];
          if (typeof connectomeDriver.stepBlocks === "function") {
            // One request per tick; the worker times every block separately.
            const msg = await connectomeDriver.stepBlocks(block, blocks, features);
            motors =
              Array.isArray(msg.motors) && msg.motors.length ? msg.motors : [msg.motor];
          } else {
            for (let i = 0; i < blocks; i += 1) {
              const msg = await connectomeDriver.step(block, features);
              motors.push(msg.motor);
            }
          }
          for (const m of motors) lastConnectomeMotor = m;
          motion._applyFlyBody(blocks * block);
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
    setRetinaPlane(plane) {
      motion.setRetinaPlane(plane);
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
