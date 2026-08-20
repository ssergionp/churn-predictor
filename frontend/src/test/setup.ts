import "@testing-library/jest-dom/vitest";

// jsdom has no ResizeObserver; recharts' ResponsiveContainer needs one to mount.
class ResizeObserverStub {
  observe() {}
  unobserve() {}
  disconnect() {}
}

globalThis.ResizeObserver ??= ResizeObserverStub;

// jsdom reports 0x0 for every element, so recharts' ResponsiveContainer
// never gets a usable width; fake a reasonable viewport size instead.
Element.prototype.getBoundingClientRect = () => ({
  width: 600,
  height: 400,
  top: 0,
  left: 0,
  right: 600,
  bottom: 400,
  x: 0,
  y: 0,
  toJSON() {},
});
