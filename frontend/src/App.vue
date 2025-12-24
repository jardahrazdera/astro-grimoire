<script setup>
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';
import { 
  Moon, 
  Sun, 
  Calendar, 
  MapPin, 
  Loader2, 
  Sparkles,
  ArrowUp,
  ArrowDown,
  Search,
  Crosshair
} from 'lucide-vue-next';

// --- State ---
const loading = ref(false);
const error = ref(null);
const astroData = ref(null);

// Form Inputs
const searchQuery = ref('Prušánky');
const lat = ref(48.85);
const lon = ref(16.98);
const date = ref(new Date().toISOString().split('T')[0]);
const isSearching = ref(false);
const showCoords = ref(false);
const locationDetails = ref(null);

// Autocomplete State
const suggestions = ref([]);
const showSuggestions = ref(false);
let debounceTimeout = null;

// --- API Calls ---

const fetchSuggestions = async () => {
  if (!searchQuery.value || searchQuery.value.length < 3) {
    suggestions.value = [];
    return;
  }
  
  try {
    const response = await axios.get('http://localhost:8000/search-location', {
      params: { q: searchQuery.value }
    });
    suggestions.value = response.data || [];
    showSuggestions.value = true;
  } catch (err) {
    console.error("Autocomplete error", err);
  }
};

const selectLocation = async (loc) => {
  searchQuery.value = loc.name;
  lat.value = loc.lat;
  lon.value = loc.lon;
  locationDetails.value = loc;
  showSuggestions.value = false;
  suggestions.value = [];
  
  await fetchData();
};

// Watch input for autocomplete
watch(searchQuery, (newVal) => {
  if (debounceTimeout) clearTimeout(debounceTimeout);
  
  // If we just selected a location (and update the query), don't re-search immediately
  // A simple check is if the new value matches the current selected location name, but 
  // users might edit it. For now, just debounce.
  
  debounceTimeout = setTimeout(() => {
    if (newVal && (!locationDetails.value || newVal !== locationDetails.value.name)) {
        fetchSuggestions();
    }
  }, 500); // 500ms debounce
});

const searchLocation = async () => {
  // If we have suggestions and the user hits enter, maybe pick the first one?
  // Or just do a hard search. Let's do a hard search which is effectively the same 
  // as the current logic but using the first result.
  if (!searchQuery.value) return;
  isSearching.value = true;
  error.value = null;
  locationDetails.value = null;
  showSuggestions.value = false; // Hide dropdown on manual search
  
  try {
    const response = await axios.get('http://localhost:8000/search-location', {
      params: { q: searchQuery.value }
    });
    
    if (response.data && response.data.length > 0) {
      const loc = response.data[0];
      lat.value = loc.lat;
      lon.value = loc.lon;
      locationDetails.value = loc;
      // Trigger astro data fetch immediately after finding location
      await fetchData();
    } else {
      error.value = "Location not found in the star charts.";
    }
  } catch (err) {
    error.value = "Could not consult the cartographer (Geocoding Error)";
    console.error(err);
  } finally {
    isSearching.value = false;
  }
};

const getUserLocation = () => {
  if (!navigator.geolocation) {
    error.value = "Your browser does not support celestial positioning.";
    return;
  }
  
  isSearching.value = true;
  error.value = null;
  locationDetails.value = null;

  navigator.geolocation.getCurrentPosition(
    async (position) => {
      try {
        const userLat = position.coords.latitude;
        const userLon = position.coords.longitude;
        
        // Reverse Geocode
        const response = await axios.get('http://localhost:8000/reverse-geocode', {
          params: { lat: userLat, lon: userLon }
        });
        
        const loc = response.data;
        lat.value = loc.lat;
        lon.value = loc.lon;
        locationDetails.value = loc;
        searchQuery.value = loc.name;
        
        await fetchData();
      } catch (err) {
         error.value = "Could not identify your realm from the stars.";
         console.error(err);
      } finally {
        isSearching.value = false;
      }
    },
    (err) => {
      error.value = "Permission to view your realm was denied.";
      isSearching.value = false;
      console.error(err);
    }
  );
};

const fetchData = async () => {
  loading.value = true;
  error.value = null;
  astroData.value = null;

  try {
    const response = await axios.get('http://localhost:8000/astro-data', {
      params: {
        lat: lat.value,
        lon: lon.value,
        date: date.value
      }
    });
    astroData.value = response.data;
  } catch (err) {
    error.value = "The stars remain silent... (Connection Error)";
    console.error(err);
  } finally {
    loading.value = false;
  }
};

// Initial fetch
onMounted(() => {
  fetchData();
});

// --- Formatters ---
const formatTime = (isoString) => {
  if (!isoString) return '--:--';
  const d = new Date(isoString);
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};
</script>

<template>
  <div class="min-h-screen bg-midnight-950 bg-star-pattern text-mystic-silver font-sans selection:bg-emerald-900 selection:text-amber-100 flex flex-col items-center p-4 sm:p-8 relative overflow-hidden">
    
    <!-- Ambient Background Glow -->
    <div class="fixed top-0 left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-emerald-900/20 blur-[120px] rounded-full pointer-events-none z-0"></div>

    <!-- Header -->
    <header class="z-10 text-center mb-10 mt-4">
      <h1 class="font-wicca text-4xl sm:text-6xl text-transparent bg-clip-text bg-gradient-to-r from-mystic-silver via-amber-100 to-mystic-silver drop-shadow-[0_0_10px_rgba(252,211,77,0.3)] mb-2">
        Astro Grimoire
      </h1>
      <p class="text-emerald-200/60 tracking-[0.2em] text-sm uppercase">Celestial Ephemeris & Lunation</p>
    </header>

    <!-- Controls / Input -->
    <section class="z-20 w-full max-w-5xl mb-12">
      <div class="glass-panel p-6 flex flex-col gap-6">
        
        <div class="flex flex-col md:flex-row gap-4">
            <!-- Search Bar -->
            <div class="flex-1 relative group">
              <label class="block text-emerald-100/50 text-xs uppercase tracking-widest mb-2 font-bold">Location</label>
              <div class="relative flex items-center">
                  <MapPin class="absolute left-3 text-emerald-500 w-4 h-4" />
                  <input 
                    v-model="searchQuery" 
                    @keyup.enter="searchLocation"
                    type="text" 
                    class="input-field pl-10 pr-20" 
                    placeholder="Enter city (e.g. Prague, Salem)" 
                  />
                  <div class="absolute right-2 flex items-center gap-1">
                      <button 
                        @click="getUserLocation"
                        class="p-1.5 rounded-md hover:bg-emerald-900/50 text-emerald-400 transition-colors"
                        title="Use my location"
                        :disabled="isSearching"
                      >
                         <Crosshair class="w-4 h-4" />
                      </button>
                      <div class="w-px h-4 bg-emerald-900/50"></div>
                      <button 
                        @click="searchLocation"
                        class="p-1.5 rounded-md hover:bg-emerald-900/50 text-emerald-400 transition-colors"
                        :disabled="isSearching"
                      >
                        <Loader2 v-if="isSearching" class="w-4 h-4 animate-spin" />
                        <Search v-else class="w-4 h-4" />
                      </button>
                  </div>
                  
                  <!-- Autocomplete Dropdown -->
                  <div v-if="showSuggestions && suggestions.length > 0" class="absolute top-full left-0 w-full mt-2 bg-midnight-950/95 border border-emerald-900/50 rounded-lg shadow-2xl z-50 overflow-hidden backdrop-blur-xl">
                    <ul>
                      <li 
                        v-for="(place, index) in suggestions" 
                        :key="index"
                        @click="selectLocation(place)"
                        class="px-4 py-3 hover:bg-emerald-900/30 cursor-pointer border-b border-white/5 last:border-none transition-colors group"
                      >
                        <div class="flex items-center gap-2">
                           <MapPin class="w-3 h-3 text-emerald-500/50 group-hover:text-emerald-400" />
                           <span class="text-emerald-100 font-wicca">{{ place.name }}</span>
                        </div>
                        <div class="text-xs text-emerald-200/40 pl-5 truncate">{{ place.display_name }}</div>
                      </li>
                    </ul>
                  </div>
              </div>
            </div>

            <!-- Date Picker -->
            <div class="w-full md:w-auto md:min-w-[200px]">
              <label class="block text-emerald-100/50 text-xs uppercase tracking-widest mb-2 font-bold">Date</label>
              <div class="relative">
                <Calendar class="absolute left-3 top-1/2 -translate-y-1/2 text-emerald-500 w-4 h-4" />
                <input v-model="date" type="date" class="input-field pl-10" />
              </div>
            </div>

             <!-- Main Action -->
            <div class="flex items-end">
                <button @click="fetchData" :disabled="loading" class="rune-button w-full md:w-auto min-w-[140px] flex items-center justify-center gap-2 h-[42px]">
                <Loader2 v-if="loading" class="animate-spin w-4 h-4" />
                <span v-else>Consult Stars</span>
                </button>
            </div>
        </div>

        <!-- Realm Details (Location Info) -->
        <div v-if="locationDetails" class="border-t border-emerald-900/30 pt-4 mt-2 animate-fade-in">
            <div class="flex items-start gap-3 text-emerald-100/80">
                <MapPin class="w-5 h-5 text-mystic-gold mt-1 shrink-0" />
                <div>
                    <h3 class="font-wicca text-xl text-mystic-gold leading-none mb-1">{{ locationDetails.name }}</h3>
                    <p class="text-xs text-emerald-200/60 font-mono mb-2">{{ locationDetails.display_name }}</p>
                    <div class="flex flex-wrap gap-2 text-xs font-bold uppercase tracking-wider">
                        <span v-if="locationDetails.country" class="px-2 py-0.5 rounded bg-emerald-900/40 text-emerald-300 border border-emerald-800/50">
                            {{ locationDetails.country }}
                        </span>
                         <span v-if="locationDetails.state" class="px-2 py-0.5 rounded bg-slate-800/40 text-slate-300 border border-slate-700/50">
                            {{ locationDetails.state }}
                        </span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Coordinates Toggle -->
        <div class="text-xs text-center">
            <button @click="showCoords = !showCoords" class="text-emerald-500/50 hover:text-emerald-400 underline decoration-dotted">
                {{ showCoords ? 'Hide Coordinates' : 'Show Coordinates' }}
            </button>
            
            <div v-if="showCoords" class="mt-2 flex justify-center gap-4 text-emerald-100/40 font-mono transition-all">
                <span>Lat: {{ lat }}</span>
                <span>Lon: {{ lon }}</span>
            </div>
        </div>

      </div>
    </section>

    <!-- Error State -->
    <div v-if="error" class="z-10 text-rose-300 bg-rose-950/30 border border-rose-900/50 p-4 rounded-lg backdrop-blur-sm mb-8">
      {{ error }}
    </div>

    <!-- Data Display -->
    <main v-if="astroData && !loading" class="z-10 w-full max-w-5xl grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-fade-in">

      <!-- Moon Phase Card (Featured) -->
      <div class="glass-panel col-span-1 md:col-span-2 lg:col-span-1 flex flex-col items-center justify-center text-center p-8 relative overflow-hidden group">
        <div class="absolute inset-0 bg-gradient-to-br from-indigo-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
        
        <h2 class="font-wicca text-2xl text-amber-100 mb-6 relative">Current Phase</h2>
        
        <!-- Simplified Moon Representation -->
        <div class="relative w-32 h-32 mb-6 rounded-full shadow-[0_0_50px_rgba(255,255,255,0.1)] bg-slate-800 border border-slate-700 flex items-center justify-center">
             <Moon class="w-16 h-16 text-mystic-silver drop-shadow-[0_0_15px_rgba(255,255,255,0.5)]" />
             <div class="absolute -bottom-2 bg-slate-900 text-xs px-2 py-1 rounded border border-slate-700">
                {{ astroData.moon_phase.illumination_percent }}%
             </div>
        </div>

        <div class="relative">
            <p class="text-xl text-white font-serif tracking-wide">{{ astroData.moon_phase.phase_name }}</p>
            <p class="text-sm text-slate-400 mt-1">Age: {{ astroData.moon_phase.age_days }} days</p>
        </div>
      </div>

      <!-- Sun Cycle -->
      <div class="glass-panel p-6 flex flex-col justify-between">
        <h3 class="font-wicca text-xl text-amber-500/80 flex items-center gap-2 mb-4">
          <Sun class="w-5 h-5" /> Sun Cycle
        </h3>
        <div class="space-y-4">
          <div class="flex justify-between items-center border-b border-white/5 pb-2">
            <span class="text-emerald-100/60 flex items-center gap-2"><ArrowUp class="w-4 h-4"/> Sunrise</span>
            <span class="font-mono text-lg">{{ format_ephem_date(astroData.sun_times.rise) }}</span>
          </div>
          <div class="flex justify-between items-center border-b border-white/5 pb-2">
            <span class="text-emerald-100/60 flex items-center gap-2"><ArrowDown class="w-4 h-4"/> Sunset</span>
            <span class="font-mono text-lg">{{ format_ephem_date(astroData.sun_times.set) }}</span>
          </div>
           <div class="mt-4 text-xs text-center text-slate-500 italic">
             {{ astroData.sun_times.is_always_up ? 'Sun is always up today' : '' }}
             {{ astroData.sun_times.is_always_down ? 'Sun is always down today' : '' }}
           </div>
        </div>
      </div>

      <!-- Moon Cycle -->
      <div class="glass-panel p-6 flex flex-col justify-between">
        <h3 class="font-wicca text-xl text-indigo-300 flex items-center gap-2 mb-4">
          <Moon class="w-5 h-5" /> Moon Cycle
        </h3>
        <div class="space-y-4">
          <div class="flex justify-between items-center border-b border-white/5 pb-2">
            <span class="text-emerald-100/60 flex items-center gap-2"><ArrowUp class="w-4 h-4"/> Moonrise</span>
            <span class="font-mono text-lg">{{ format_ephem_date(astroData.moon_times.rise) }}</span>
          </div>
          <div class="flex justify-between items-center border-b border-white/5 pb-2">
            <span class="text-emerald-100/60 flex items-center gap-2"><ArrowDown class="w-4 h-4"/> Moonset</span>
            <span class="font-mono text-lg">{{ format_ephem_date(astroData.moon_times.set) }}</span>
          </div>
          <div class="mt-4 text-xs text-center text-slate-500 italic">
             {{ astroData.moon_times.is_always_up ? 'Moon is always up today' : '' }}
             {{ astroData.moon_times.is_always_down ? 'Moon is always down today' : '' }}
           </div>
        </div>
      </div>

      <!-- Solstices (Full Width) -->
      <div class="glass-panel col-span-1 md:col-span-2 lg:col-span-3 p-6 flex flex-col md:flex-row justify-around items-center gap-6 mt-4">
        <div class="text-center">
            <div class="text-xs uppercase tracking-widest text-emerald-500 mb-1">Summer Solstice</div>
            <div class="font-wicca text-xl text-amber-100">{{ formatDate(astroData.solstices_current_year.summer_solstice) }}</div>
        </div>
        <div class="h-px w-20 bg-emerald-900 md:h-10 md:w-px"></div>
        <div class="text-center">
             <div class="text-xs uppercase tracking-widest text-emerald-500 mb-1">Hemisphere</div>
             <div class="font-wicca text-xl text-mystic-silver">{{ astroData.solstices_current_year.hemisphere }}</div>
        </div>
        <div class="h-px w-20 bg-emerald-900 md:h-10 md:w-px"></div>
        <div class="text-center">
            <div class="text-xs uppercase tracking-widest text-emerald-500 mb-1">Winter Solstice</div>
            <div class="font-wicca text-xl text-blue-100">{{ formatDate(astroData.solstices_current_year.winter_solstice) }}</div>
        </div>
      </div>

    </main>

  </div>
</template>

<script>
// Non-setup script for simple helper if needed, but we can do it in setup.
// Defining helpers in setup for cleaner template usage.
const format_ephem_date = (iso) => {
    if (!iso) return '--:--';
    return new Date(iso).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
}
const formatDate = (iso) => {
    if (!iso) return '---';
    return new Date(iso).toLocaleDateString([], { month: 'long', day: 'numeric' });
}
</script>

<style scoped>
/* Custom Utilities for Glassmorphism & Wicca Theme */

.glass-panel {
  @apply bg-midnight-900/60 backdrop-blur-md border border-emerald-900/30 rounded-xl shadow-2xl transition-all duration-300 hover:border-emerald-500/30 hover:shadow-[0_0_30px_rgba(16,185,129,0.1)];
}

.input-field {
  @apply w-full bg-black/40 border border-emerald-900/50 rounded-lg py-2.5 pr-4 text-emerald-100 placeholder-emerald-800/50 focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/50 transition-all font-mono text-sm;
}

/* Chrome/Safari/Edge date input styling fix for dark mode */
.input-field::-webkit-calendar-picker-indicator {
    filter: invert(1) opacity(0.5);
    cursor: pointer;
}

.rune-button {
  @apply bg-emerald-900/40 hover:bg-emerald-800/60 text-emerald-100 border border-emerald-700/50 px-6 py-2.5 rounded-lg uppercase tracking-widest text-xs font-bold transition-all hover:shadow-[0_0_15px_rgba(16,185,129,0.2)] active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed;
}

.animate-fade-in {
  animation: fadeIn 1s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
