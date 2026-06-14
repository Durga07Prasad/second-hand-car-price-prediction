/**
 * AnimatedCounter — Counts up from 0 to a target value over ~1.5s.
 * Formats the number as Indian currency (₹ with lakhs/crores separators).
 */
import { useEffect, useRef, useState } from 'react';
import { motion, useInView } from 'framer-motion';

/**
 * Format a number in Indian numbering system.
 * e.g., 303900 → "3,03,900"
 */
function formatIndianNumber(num) {
  const n = Math.round(num);
  const str = n.toString();
  if (str.length <= 3) return str;

  // Last 3 digits
  let result = str.slice(-3);
  let remaining = str.slice(0, -3);

  // Group remaining digits in pairs from right
  while (remaining.length > 0) {
    const chunk = remaining.slice(-2);
    result = chunk + ',' + result;
    remaining = remaining.slice(0, -2);
  }

  return result;
}

export default function AnimatedCounter({
  target = 0,
  prefix = '₹',
  suffix = '',
  duration = 1.5,
  className = '',
  triggerOnView = true,
}) {
  const [count, setCount] = useState(0);
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-50px' });
  const hasStarted = useRef(false);

  useEffect(() => {
    // Only animate when in view (or immediately if triggerOnView is false)
    const shouldStart = triggerOnView ? isInView : true;
    if (!shouldStart || hasStarted.current || target === 0) return;

    hasStarted.current = true;
    const startTime = performance.now();
    const startVal = 0;
    const endVal = target;

    function animate(currentTime) {
      const elapsed = (currentTime - startTime) / 1000; // seconds
      const progress = Math.min(elapsed / duration, 1);

      // Ease-out cubic for smooth deceleration
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = startVal + (endVal - startVal) * eased;

      setCount(current);

      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        setCount(endVal);
      }
    }

    requestAnimationFrame(animate);
  }, [isInView, target, duration, triggerOnView]);

  // Reset when target changes
  useEffect(() => {
    hasStarted.current = false;
    setCount(0);
  }, [target]);

  return (
    <motion.span
      ref={ref}
      className={className}
      initial={{ opacity: 0, scale: 0.5 }}
      animate={isInView || !triggerOnView ? { opacity: 1, scale: 1 } : {}}
      transition={{ duration: 0.4, ease: 'easeOut' }}
    >
      {prefix}{formatIndianNumber(count)}{suffix}
    </motion.span>
  );
}
