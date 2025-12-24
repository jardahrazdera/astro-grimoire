/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'wicca': ['"Cinzel"', 'serif'],
        'sans': ['"Lato"', 'sans-serif'],
      },
      colors: {
        midnight: {
          900: '#020617', // deeply dark blue
          950: '#0b0d14', // almost black
        },
        mystic: {
          gold: '#fcd34d',
          silver: '#e2e8f0',
        }
      },
      backgroundImage: {
        'star-pattern': "radial-gradient(white, rgba(255,255,255,.2) 2px, transparent 3px), radial-gradient(white, rgba(255,255,255,.15) 1px, transparent 2px), radial-gradient(white, rgba(255,255,255,.1) 2px, transparent 3px)",
      }
    },
  },
  plugins: [],
}
