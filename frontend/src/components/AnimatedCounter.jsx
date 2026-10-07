import { useState, useEffect, useRef } from 'react';

export default function AnimatedCounter({ value, duration = 1200, prefix = '', suffix = '', className = '' }) {
  const [display, setDisplay] = useState(0);
  const startRef = useRef(null);
  const prevRef = useRef(0);

  useEffect(() => {
    const target = typeof value === 'number' ? value : parseFloat(value) || 0;
    const start = prevRef.current;
    const diff = target - start;

    if (diff === 0) return;

    startRef.current = performance.now();

    const animate = (now) => {
      const elapsed = now - startRef.current;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = start + diff * eased;

      setDisplay(current);

      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        prevRef.current = target;
      }
    };

    requestAnimationFrame(animate);
  }, [value, duration]);

  const formatted = Number.isInteger(value)
    ? Math.round(display).toLocaleString()
    : display.toFixed(1);

  return (
    <span className={`tabular-nums ${className}`}>
      {prefix}{formatted}{suffix}
    </span>
  );
}
