<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';

const now = ref(new Date());
let timer = null;

const updateTime = () => {
  now.value = new Date();
};

onMounted(() => {
  timer = setInterval(updateTime, 1000);
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
});

// --- Formatters ---

// "WEDNESDAY, THE 24TH OF DECEMBER"
const formattedDate = computed(() => {
  const d = now.value;
  const dayName = d.toLocaleDateString('en-US', { weekday: 'long' });
  const monthName = d.toLocaleDateString('en-US', { month: 'long' });
  const dayNum = d.getDate();
  
  // Ordinal suffix logic
  const j = dayNum % 10,
        k = dayNum % 100;
  let suffix = "th";
  if (j == 1 && k != 11) { suffix = "st"; }
  else if (j == 2 && k != 12) { suffix = "nd"; }
  else if (j == 3 && k != 13) { suffix = "rd"; }
  
  return `${dayName}, the ${dayNum}${suffix} of ${monthName}`.toUpperCase();
});

const formattedTime = computed(() => {
  return now.value.toLocaleTimeString('en-US', { 
    hour12: false, 
    hour: '2-digit', 
    minute: '2-digit' 
  });
});

const timePhase = computed(() => {
  const h = now.value.getHours();
  
  if (h >= 0 && h < 3) return "The Silent Watch";
  if (h >= 3 && h < 6) return "Before the Dawn";
  if (h >= 6 && h < 12) return "Morning's Ascent";
  if (h >= 12 && h < 14) return "Sun's Zenith"; // Noon specific
  if (h >= 14 && h < 17) return "Sun's Dominion";
  if (h >= 17 && h < 20) return "Evening's Embrace"; // Sunset-ish
  if (h >= 20 && h < 22) return "Twilight's Deep";
  return "Night's Depth";
});

</script>

<template>
  <div class="flex flex-col items-center justify-center text-center animate-fade-in py-4 select-none cursor-default">
    
    <!-- Date Line -->
    <div class="text-emerald-500/60 text-[10px] sm:text-xs uppercase tracking-[0.3em] font-bold mb-2">
      {{ formattedDate }}
    </div>

    <!-- Time Display -->
    <div class="relative group">
        <div class="font-wicca text-4xl sm:text-5xl text-mystic-silver drop-shadow-[0_0_10px_rgba(226,232,240,0.2)] transition-colors duration-700 group-hover:text-amber-100">
            <!-- Split time to animate colon? Or just keep simple text. Simple text is cleaner for alignment. -->
            {{ formattedTime }}
        </div>
        
        <!-- Decorative Lines -->
        <div class="absolute -left-8 top-1/2 w-6 h-px bg-gradient-to-l from-emerald-500/50 to-transparent"></div>
        <div class="absolute -right-8 top-1/2 w-6 h-px bg-gradient-to-r from-emerald-500/50 to-transparent"></div>
    </div>

    <!-- Poetic Phase -->
    <div class="mt-2 text-amber-200/80 font-serif italic text-sm tracking-wide flex items-center gap-2">
        <span class="w-1 h-1 rounded-full bg-amber-500/50"></span>
        {{ timePhase }}
        <span class="w-1 h-1 rounded-full bg-amber-500/50"></span>
    </div>

  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 1.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-5px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
