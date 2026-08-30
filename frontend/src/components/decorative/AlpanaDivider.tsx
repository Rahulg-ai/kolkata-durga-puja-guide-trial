/* =====================================================
   ALPANA DIVIDER

   A thin decorative rule inspired by alpana — the
   rice-paste line art drawn on thresholds to mark the
   passage into a sacred space. Used between sections
   instead of a plain <hr>.
   ===================================================== */

type AlpanaDividerProps = {
  className?: string;
};

function AlpanaDivider({ className = "" }: AlpanaDividerProps) {
  return (
    <svg
      className={`alpana-divider ${className}`}
      viewBox="0 0 600 40"
      preserveAspectRatio="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <path
        d="M0 20 H 250"
        stroke="var(--color-gold)"
        strokeOpacity="0.5"
        strokeWidth="1.5"
      />
      <path
        d="M350 20 H 600"
        stroke="var(--color-gold)"
        strokeOpacity="0.5"
        strokeWidth="1.5"
      />

      <g stroke="var(--color-gold)" strokeWidth="1.5" fill="none" strokeOpacity="0.85">
        <path d="M270 20 Q 285 4 300 20 Q 315 36 330 20" />
      </g>

      <circle cx="300" cy="20" r="5" fill="var(--color-sindoor)" />
      <circle cx="270" cy="20" r="3" fill="var(--color-gold)" />
      <circle cx="330" cy="20" r="3" fill="var(--color-gold)" />
      <circle cx="245" cy="20" r="2.5" fill="var(--color-gold)" fillOpacity="0.8" />
      <circle cx="355" cy="20" r="2.5" fill="var(--color-gold)" fillOpacity="0.8" />
    </svg>
  );
}

export default AlpanaDivider;