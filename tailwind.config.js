module.exports = {
  content: [
    "./templates/**/*.html",
    "./**/templates/**/*.html",
    "./static/**/*.js",
  ],
theme: {
  extend: {
    
  container: {
    center: true,
    padding: "2.5rem",
    screens: {
      xl: "1400px",
    },
  },

  keyframes: {
    fadeUp: {
      "0%": { opacity: 0, transform: "translateY(24px)" },
      "100%": { opacity: 1, transform: "translateY(0)" },
    },
  },

  animation: {
    "fade-up": "fadeUp 0.9s ease-out forwards",
  },

  transitionDelay: {
    100: "100ms",
    200: "200ms",
    300: "300ms",
  },
},

  },
  plugins: [],
}

