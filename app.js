const screenSlot = document.querySelector(".screen-slot");
const artboard = document.querySelector(".desktop-artboard");
const gameMount = document.querySelector("#game");

const FRAME_DURATION = 1000 / 60;
const DEADZONE = 0.45;

const keymap = {
  up: "ArrowUp",
  down: "ArrowDown",
  left: "ArrowLeft",
  right: "ArrowRight",
  a: "KeyA",
  b: "KeyS",
  c: "KeyD",
  x: "KeyQ",
  y: "KeyW",
  z: "KeyE",
  start: "Enter",
  mode: "KeyZ",
};

const gamepadMap = {
  0: "b",
  1: "a",
  2: "x",
  3: "y",
  4: "c",
  5: "z",
  8: "mode",
  9: "start",
  12: "up",
  13: "down",
  14: "left",
  15: "right",
};

let emulatorRunning = false;
let gamepadPoll = null;
let gamepadPrevious = {};
let axesPrevious = {
  up: false,
  down: false,
  left: false,
  right: false,
};

window.TotoniaDemo = {
  screenSlot,
  artboard,
  gameMount,
  mountSelector: "#game",
  romUrl: "./roms/totonia-demo.bin",
  emulator: {
    engine: "Genesis.js",
    core: "PicoDrive",
    container: "game",
  },
  markEmulatorReady() {
    artboard?.classList.add("is-emulator-ready");
    screenSlot?.classList.add("is-emulator-ready");
  },
  markEmulatorError(error) {
    console.error("Totonia emulator failed to load", error);
    artboard?.classList.add("is-emulator-error");
  },
};

const keyValue = (code) => {
  const values = {
    ArrowUp: "ArrowUp",
    ArrowDown: "ArrowDown",
    ArrowLeft: "ArrowLeft",
    ArrowRight: "ArrowRight",
    Enter: "Enter",
    Space: " ",
  };

  if (values[code]) {
    return values[code];
  }

  if (code.startsWith("Key")) {
    return code.slice(3).toLowerCase();
  }

  if (code.startsWith("Digit")) {
    return code.slice(5);
  }

  return code;
};

const dispatchKey = (code, pressed) => {
  document.dispatchEvent(
    new KeyboardEvent(pressed ? "keydown" : "keyup", {
      code,
      key: keyValue(code),
      bubbles: true,
      cancelable: true,
    }),
  );
};

const actionToKey = (action) => keymap[action] || null;

const pollGamepad = () => {
  if (!emulatorRunning) {
    return;
  }

  const gamepad = [...(navigator.getGamepads ? navigator.getGamepads() : [])]
    .find((candidate) => candidate?.connected);

  if (!gamepad) {
    return;
  }

  gamepad.buttons.forEach((button, index) => {
    const pressed = button.pressed || button.value > 0.5;
    const code = actionToKey(gamepadMap[index]);

    if (!code) {
      return;
    }

    if (pressed && !gamepadPrevious[index]) {
      dispatchKey(code, true);
    }

    if (!pressed && gamepadPrevious[index]) {
      dispatchKey(code, false);
    }

    gamepadPrevious[index] = pressed;
  });

  const axisX = gamepad.axes[0] || 0;
  const axisY = gamepad.axes[1] || 0;
  const axes = {
    left: axisX < -DEADZONE,
    right: axisX > DEADZONE,
    up: axisY < -DEADZONE,
    down: axisY > DEADZONE,
  };

  Object.entries(axes).forEach(([action, pressed]) => {
    const code = actionToKey(action);

    if (!code) {
      return;
    }

    if (pressed && !axesPrevious[action]) {
      dispatchKey(code, true);
    }

    if (!pressed && axesPrevious[action]) {
      dispatchKey(code, false);
    }
  });

  axesPrevious = axes;
};

const startGamepadPolling = () => {
  stopGamepadPolling();
  gamepadPoll = window.setInterval(pollGamepad, FRAME_DURATION);
};

const stopGamepadPolling = () => {
  if (gamepadPoll) {
    window.clearInterval(gamepadPoll);
  }

  gamepadPoll = null;
  gamepadPrevious = {};
  axesPrevious = {
    up: false,
    down: false,
    left: false,
    right: false,
  };
};

const focusEmulatorCanvas = () => {
  const canvas = gameMount?.querySelector("canvas");

  if (!canvas) {
    return;
  }

  canvas.tabIndex = 0;
  canvas.focus({ preventScroll: true });
};

const mountGenesis = (romBuffer) => {
  if (typeof window.embedGenesis !== "function") {
    window.TotoniaDemo.markEmulatorError(
      new Error("Missing local Genesis.js engine"),
    );
    return;
  }

  window.embedGenesis({
    container: window.TotoniaDemo.emulator.container,
    name: "Totonia Demo",
    rom: romBuffer,
    soundEnabled: true,
    showMobileControls: false,
    player1: {
      up: keymap.up,
      down: keymap.down,
      left: keymap.left,
      right: keymap.right,
      start: keymap.start,
      mode: keymap.mode,
      a: keymap.a,
      b: keymap.b,
      c: keymap.c,
      x: keymap.x,
      y: keymap.y,
      z: keymap.z,
    },
    cbStarted: () => {
      emulatorRunning = true;
      window.TotoniaDemo.markEmulatorReady();
      focusEmulatorCanvas();
      startGamepadPolling();
    },
  });
};

const loadRom = async () => {
  if (!gameMount) {
    return;
  }

  try {
    const response = await fetch(window.TotoniaDemo.romUrl, {
      cache: "no-store",
    });

    if (!response.ok) {
      throw new Error(`ROM request failed with HTTP ${response.status}`);
    }

    mountGenesis(await response.arrayBuffer());
  } catch (error) {
    window.TotoniaDemo.markEmulatorError(error);
  }
};

window.addEventListener(
  "keydown",
  (event) => {
    if (!emulatorRunning) {
      return;
    }

    if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", " "].includes(event.key)) {
      event.preventDefault();
    }
  },
  { passive: false },
);

gameMount?.addEventListener("pointerdown", focusEmulatorCanvas);
window.addEventListener("beforeunload", stopGamepadPolling);

loadRom();
