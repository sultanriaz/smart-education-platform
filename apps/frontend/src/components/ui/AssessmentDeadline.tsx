import { useEffect, useRef, useState } from "react";

export function AssessmentDeadline({ expiresAt, serverTime, onExpire }: { expiresAt: string; serverTime?: string | null; onExpire: () => void }) {
  const offset = useRef(serverTime ? new Date(serverTime).getTime() - Date.now() : 0);
  const [current, setCurrent] = useState(() => Date.now() + offset.current);
  const fired = useRef(false);
  const deadline = new Date(expiresAt).getTime();
  const remaining = Math.max(0, Math.ceil((deadline - current) / 1000));

  useEffect(() => {
    const timer = window.setInterval(() => setCurrent(Date.now() + offset.current), 500);
    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => {
    if (remaining === 0 && !fired.current) {
      fired.current = true;
      onExpire();
    }
  }, [remaining, onExpire]);

  return (
    <span role="timer" aria-label="Assessment time remaining" className={remaining <= 60 ? "font-semibold text-danger" : "font-medium"}>
      {Math.floor(remaining / 60)}:{String(remaining % 60).padStart(2, "0")} remaining
    </span>
  );
}
