/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        rzpDark: '#0e0b08',
        rzpSurface: '#161310',
        rzpGold: '#E5A93C',
        rzpBlue: '#0C65FF',
      },
      fontFamily: {
        sans: ['Satoshi', 'Lato', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      }
    },
  },
  plugins: [],
}
