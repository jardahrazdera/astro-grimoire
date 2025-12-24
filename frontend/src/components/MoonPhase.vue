<script setup>
import { computed } from 'vue';

const props = defineProps({
  percent: {
    type: Number,
    required: true,
    default: 0
  },
  phase: {
    type: String,
    default: 'New Moon'
  },
  hemisphere: {
    type: String,
    default: 'Northern'
  }
});

const isWaxing = computed(() => {
  const p = props.phase.toLowerCase();
  return p.includes('waxing') || p.includes('first');
});

const pathD = computed(() => {
  // SVG viewbox 0 0 100 100. Center 50 50. Radius 45.
  // We draw the LIT part.
  
  // Normalize percent 0-100 to 0-1
  const p = props.percent / 100;
  
  // Determine if lit side is Right (Waxing N, Waning S) or Left (Waning N, Waxing S)
  // Standard Northern: Waxing = Right lit. Waning = Left lit.
  let litRight = isWaxing.value;
  if (props.hemisphere === 'Southern') {
    litRight = !litRight;
  }
  
  // Full Moon or New Moon - handle simply by circle opacity or overlay
  if (p >= 0.99) return 'M 50,5 A 45,45 0 1,1 50,95 A 45,45 0 1,1 50,5'; // Full circle
  if (p <= 0.01) return ''; // Empty path
  
  // Calculate the curve
  // The curve is an elliptical arc. 
  // The 'width' of the ellipse depends on deviation from 50%.
  // 50% = 0 width (straight line). 0/100% = full width.
  
  // x-radius of the terminator ellipse. 
  // At 50%, rx = 0. At 0% or 100%, rx = 45.
  // Formula: rx = 45 * 2 * |0.5 - p|
  const rx = 45 * 2 * Math.abs(0.5 - p);
  
  // Sweep flag for arc: depends on whether we are > 50% or < 50%
  // And which side is lit.
  
  // Let's construct the path for the Lit Area.
  // It's always composed of two arcs:
  // 1. The outer circle arc (half-circle).
  // 2. The terminator arc.
  
  // Points: Top (50, 5), Bottom (50, 95).
  
  // Directions:
  // Right Lit: Outer arc is (50,5) -> (95,50) -> (50,95). Sweep 1.
  // Left Lit: Outer arc is (50,95) -> (5,50) -> (50,5). Sweep 1.
  
  const outerSweep = 1;
  const outerArc = litRight 
    ? `M 50,5 A 45,45 0 0,1 50,95` 
    : `M 50,95 A 45,45 0 0,1 50,5`;
    
  // Terminator Arc:
  // Connects the two ends of the outer arc back to start.
  // If Lit Right: (50,95) back to (50,5).
  // If Lit Left: (50,5) back to (50,95).
  
  // Sweep depends on Gibbous vs Crescent.
  // Gibbous (>50%): Terminator bulges OUTWARD (convex).
  // Crescent (<50%): Terminator bulges INWARD (concave).
  
  // If Lit Right (Waxing N):
  // Crescent (p<0.5): Inner curve matches outer circle side (concave). Sweep 0.
  // Gibbous (p>0.5): Inner curve bulges left (convex). Sweep 1.
  
  let innerSweep = 0;
  if (p > 0.5) innerSweep = 1; 
  if (!litRight) innerSweep = innerSweep ? 0 : 1; // Invert for Left lit
  
  const terminator = `A ${rx},45 0 0,${innerSweep} ${litRight ? '50,5' : '50,95'}`;
  
  return `${outerArc} ${terminator} Z`;
});

</script>

<template>
  <div class="relative w-full h-full flex items-center justify-center">
    <svg viewBox="0 0 100 100" class="w-full h-full drop-shadow-[0_0_15px_rgba(255,255,255,0.3)]">
        <!-- Background (Shadow part) -->
        <circle cx="50" cy="50" r="45" class="fill-slate-900 stroke-slate-700 stroke-[0.5]" />
        
        <!-- Lit part -->
        <path :d="pathD" class="fill-mystic-silver transition-all duration-1000 ease-out" />
        
        <!-- Crater Texture Overlay (Optional, simple noise) -->
        <filter id="noise">
            <feTurbulence type="fractalNoise" baseFrequency="0.6" numOctaves="3" stitchTiles="stitch" />
            <feColorMatrix type="saturate" values="0" />
            <feComponentTransfer>
                <feFuncA type="linear" slope="0.3" /> <!-- Reduce opacity of noise -->
            </feComponentTransfer>
            <feComposite operator="in" in2="SourceGraphic" />
        </filter>
        
        <circle cx="50" cy="50" r="45" filter="url(#noise)" class="fill-transparent opacity-30 pointer-events-none" />
    </svg>
  </div>
</template>
