/* =====================================================
   DURGA MOTIF

   A stylised, line-art rendering of Maa Durga's eyes
   and mukut (crown) — the iconic minimal mark used on
   pandal gates and Puja hoardings across Kolkata.

   Deliberately abstract: two winged, lotus-shaped eyes
   and a three-peaked crown, drawn as gold linework on
   the page background. Not a literal face — this is
   the same level of abstraction as the real hoardings.

   Colour comes entirely from CSS variables, so it
   re-themes with the rest of the app automatically.
   ===================================================== */

type DurgaMotifProps = {
  className?: string;
};

function DurgaMotif({ className = "" }: DurgaMotifProps) {
  return (
    <svg
      className={`durga-motif ${className}`}
      viewBox="0 0 480 300"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      role="img"
      aria-label="Decorative illustration of Durga's eyes and crown"
    >
      <defs>
        <radialGradient id="motifHalo" cx="50%" cy="38%" r="65%">
          <stop offset="0%" stopColor="var(--color-gold-light)" stopOpacity="0.35" />
          <stop offset="60%" stopColor="var(--color-gold)" stopOpacity="0.08" />
          <stop offset="100%" stopColor="var(--color-gold)" stopOpacity="0" />
        </radialGradient>

        <linearGradient id="motifGold" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="var(--color-gold-light)" />
          <stop offset="100%" stopColor="var(--color-gold)" />
        </linearGradient>

        <radialGradient id="motifIris" cx="35%" cy="30%" r="75%">
          <stop offset="0%" stopColor="var(--color-indigo-light)" />
          <stop offset="100%" stopColor="var(--color-indigo)" />
        </radialGradient>
      </defs>

      {/* ambient halo */}
      <circle cx="240" cy="140" r="175" fill="url(#motifHalo)" />

      {/* radiating chalchitra rays */}
      <g className="motif-rays" stroke="var(--color-gold)" strokeOpacity="0.28" strokeWidth="1.5">
        <path d="M240 10 V 40" />
        <path d="M150 22 L 162 50" />
        <path d="M330 22 L 318 50" />
        <path d="M80 55 L 100 78" />
        <path d="M400 55 L 380 78" />
        <path d="M40 115 L 68 122" />
        <path d="M440 115 L 412 122" />
      </g>

      {/* crown / mukut */}
      <g className="motif-crown">
        <path
          d="M120 118 Q240 78 360 118"
          stroke="url(#motifGold)"
          strokeWidth="5"
          strokeLinecap="round"
        />
        <path
          d="M120 118 Q240 100 360 118 L360 130 Q240 112 120 130 Z"
          fill="url(#motifGold)"
          fillOpacity="0.9"
        />

        {/* side peaks */}
        <path d="M148 118 L162 78 L178 118 Z" fill="url(#motifGold)" />
        <path d="M302 118 L318 78 L332 118 Z" fill="url(#motifGold)" />
        <circle cx="162" cy="74" r="6" fill="var(--color-gold-light)" stroke="var(--color-maroon)" strokeWidth="2" />
        <circle cx="318" cy="74" r="6" fill="var(--color-gold-light)" stroke="var(--color-maroon)" strokeWidth="2" />

        {/* centre peak */}
        <path d="M212 118 L240 46 L268 118 Z" fill="url(#motifGold)" />
        <circle cx="240" cy="40" r="9" fill="var(--color-sindoor)" stroke="var(--color-gold-light)" strokeWidth="3" />
      </g>

      {/* tilak between the brows */}
      <path
        d="M240 148 C 235 158, 235 168, 240 174 C 245 168, 245 158, 240 148 Z"
        fill="var(--color-sindoor)"
        stroke="var(--color-gold)"
        strokeWidth="1.5"
      />

      {/* ===================== LEFT EYE ===================== */}
      <g className="motif-eye">
        {/* brow */}
        <path
          d="M96 152 Q 165 122 224 146"
          stroke="url(#motifGold)"
          strokeWidth="4"
          strokeLinecap="round"
        />

        {/* winged flick */}
        <path
          d="M100 196 C 76 182, 58 168, 40 150"
          stroke="var(--color-maroon)"
          strokeWidth="6"
          strokeLinecap="round"
        />

        {/* almond eye */}
        <path
          d="M100 196 Q135 158 176 152 Q206 148 226 178 Q196 210 158 216 Q124 220 100 196 Z"
          fill="var(--color-shola)"
          stroke="var(--color-maroon)"
          strokeWidth="5"
        />

        <circle cx="176" cy="184" r="19" fill="url(#motifIris)" />
        <circle cx="176" cy="184" r="21" fill="none" stroke="var(--color-gold)" strokeWidth="2" />
        <circle cx="170" cy="177" r="4" fill="var(--color-shola)" />
      </g>

      {/* ===================== RIGHT EYE (mirrored) ===================== */}
      <g className="motif-eye" transform="translate(480,0) scale(-1,1)">
        <path
          d="M96 152 Q 165 122 224 146"
          stroke="url(#motifGold)"
          strokeWidth="4"
          strokeLinecap="round"
        />
        <path
          d="M100 196 C 76 182, 58 168, 40 150"
          stroke="var(--color-maroon)"
          strokeWidth="6"
          strokeLinecap="round"
        />
        <path
          d="M100 196 Q135 158 176 152 Q206 148 226 178 Q196 210 158 216 Q124 220 100 196 Z"
          fill="var(--color-shola)"
          stroke="var(--color-maroon)"
          strokeWidth="5"
        />
        <circle cx="176" cy="184" r="19" fill="url(#motifIris)" />
        <circle cx="176" cy="184" r="21" fill="none" stroke="var(--color-gold)" strokeWidth="2" />
        <circle cx="170" cy="177" r="4" fill="var(--color-shola)" />
      </g>

      {/* paisley / kolka flourishes */}
      <g stroke="var(--color-gold)" strokeOpacity="0.55" strokeWidth="2" fill="none">
        <path d="M32 210 Q10 200 14 178 Q28 186 32 210 Z" />
        <path d="M448 210 Q470 200 466 178 Q452 186 448 210 Z" />
      </g>

      {/* alpana dots along the base */}
      <g fill="var(--color-gold)" fillOpacity="0.6">
        <circle cx="140" cy="252" r="3" />
        <circle cx="168" cy="262" r="3.5" />
        <circle cx="200" cy="268" r="4" />
        <circle cx="240" cy="271" r="4.5" />
        <circle cx="280" cy="268" r="4" />
        <circle cx="312" cy="262" r="3.5" />
        <circle cx="340" cy="252" r="3" />
      </g>
    </svg>
  );
}

export default DurgaMotif;