<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useI18n } from 'vue-i18n';

const { t, locale } = useI18n();
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

const formattedDate = computed(() => {
  const d = now.value;
  const lang = locale.value === 'cs' ? 'cs-CZ' : 'en-US';
  const dayName = d.toLocaleDateString(lang, { weekday: 'long' });
  const monthName = d.toLocaleDateString(lang, { month: 'long' });
  const dayNum = d.getDate();
  
  if (locale.value === 'cs') {
     return t('clock.the_of', { day: dayName, num: dayNum, month: monthName }).toUpperCase();
  }

  // Ordinal suffix logic for English
  const j = dayNum % 10,
        k = dayNum % 100;
  let suffix = "th";
  if (j == 1 && k != 11) { suffix = "st"; }
  else if (j == 2 && k != 12) { suffix = "nd"; }
  else if (j == 3 && k != 13) { suffix = "rd"; }
  
  return t('clock.the_of', { day: dayName, num: dayNum + suffix, month: monthName }).toUpperCase();
});

const formattedTime = computed(() => {
  return now.value.toLocaleTimeString(locale.value === 'cs' ? 'cs-CZ' : 'en-US', { 
    hour12: false, 
    hour: '2-digit', 
    minute: '2-digit' 
  });
});

const timePhase = computed(() => {
  const h = now.value.getHours();
  
  if (h >= 0 && h < 3) return t('clock.phases.silent_watch');
  if (h >= 3 && h < 6) return t('clock.phases.before_dawn');
  if (h >= 6 && h < 12) return t('clock.phases.morning_ascent');
  if (h >= 12 && h < 14) return t('clock.phases.suns_zenith');
  if (h >= 14 && h < 17) return t('clock.phases.suns_dominion');
  if (h >= 17 && h < 20) return t('clock.phases.evenings_embrace');
  if (h >= 20 && h < 22) return t('clock.phases.twilights_deep');
  return t('clock.phases.nights_depth');
});

</script>

<template>
  <div class="flex flex-col items-center justify-center text-center animate-fade-in py-4 select-none cursor-default relative z-10">
    
    <!-- Date Line -->
    <div class="text-emerald-500/60 text-[10px] sm:text-xs uppercase tracking-[0.3em] font-bold mb-2">
      {{ formattedDate }}
    </div>

    <!-- Time Display -->
    <div class="relative group">
        <div class="font-wicca text-4xl sm:text-5xl text-mystic-silver drop-shadow-[0_0_10px_rgba(226,232,240,0.2)] transition-colors duration-700 group-hover:text-amber-100">
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