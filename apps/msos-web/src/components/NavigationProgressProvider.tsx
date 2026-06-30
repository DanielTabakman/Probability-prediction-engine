"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { usePathname } from "next/navigation";

import { NavigationProgressBar } from "@/components/NavigationProgressBar";

type NavigationProgressContextValue = {
  start: () => void;
};

const NavigationProgressContext = createContext<NavigationProgressContextValue>({
  start: () => {},
});

export function useNavigationProgress(): NavigationProgressContextValue {
  return useContext(NavigationProgressContext);
}

export function NavigationProgressProvider({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const [active, setActive] = useState(false);
  const [progress, setProgress] = useState(0);
  const timersRef = useRef<number[]>([]);
  const navStartedRef = useRef(false);
  const pathnameAtStartRef = useRef<string | null>(null);

  const clearTimers = useCallback(() => {
    for (const id of timersRef.current) {
      window.clearTimeout(id);
    }
    timersRef.current = [];
  }, []);

  const start = useCallback(() => {
    clearTimers();
    navStartedRef.current = true;
    pathnameAtStartRef.current = pathname;
    setActive(true);
    setProgress(14);
    timersRef.current.push(window.setTimeout(() => setProgress(48), 100));
    timersRef.current.push(window.setTimeout(() => setProgress(72), 380));
    timersRef.current.push(window.setTimeout(() => setProgress(88), 900));
  }, [clearTimers, pathname]);

  const finish = useCallback(() => {
    if (!navStartedRef.current) {
      return;
    }
    navStartedRef.current = false;
    pathnameAtStartRef.current = null;
    clearTimers();
    setProgress(100);
    timersRef.current.push(
      window.setTimeout(() => {
        setActive(false);
        setProgress(0);
      }, 280),
    );
  }, [clearTimers]);

  useEffect(() => {
    if (!navStartedRef.current || pathname === pathnameAtStartRef.current) {
      return;
    }
    finish();
  }, [pathname, finish]);

  useEffect(() => () => clearTimers(), [clearTimers]);

  return (
    <NavigationProgressContext.Provider value={{ start }}>
      <NavigationProgressBar active={active} progress={progress} />
      {children}
    </NavigationProgressContext.Provider>
  );
}
