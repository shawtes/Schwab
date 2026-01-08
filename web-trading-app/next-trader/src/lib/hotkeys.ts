"use client";

import { useEffect } from "react";

type HotkeyMap = Record<string, () => void>;

const isMeta = (event: KeyboardEvent) => event.metaKey || event.ctrlKey;

export function useHotkeys(map: HotkeyMap) {
  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      const key = event.key.toLowerCase();
      if (map[key]) {
        // prevent typing side-effects when shortcut is intended
        if (!["input", "textarea"].includes((event.target as HTMLElement).tagName.toLowerCase())) {
          event.preventDefault();
        }
        map[key]?.();
      }
      if ((key === "k" && isMeta(event)) && map["cmd+k"]) {
        event.preventDefault();
        map["cmd+k"]?.();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [map]);
}

