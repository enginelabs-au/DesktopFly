/**
 * Window layer ordering / occlusion helpers (desktop shell).
 */

export class LayerStack {
  constructor() {
    this._order = [];
  }

  setOrder(windowIds) {
    if (!Array.isArray(windowIds)) throw new Error("windowIds must be array");
    this._order = windowIds.map(String);
  }

  isOccluded(petWindowId, hostWindowId) {
    const pet = this._order.indexOf(String(petWindowId));
    const host = this._order.indexOf(String(hostWindowId));
    if (pet < 0 || host < 0) return false;
    return pet < host; // higher index = closer to front in this model
  }

  order() {
    return [...this._order];
  }
}
