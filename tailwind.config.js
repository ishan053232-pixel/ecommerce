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
    animation: {
      fade: "fadeIn 1s ease-out forwards",
      slide: "slideUp 0.8s ease-out forwards",
    },
    keyframes: {
      fadeIn: {
        "0%": { opacity: 0 },
        "100%": { opacity: 1 },
      },
      slideUp: {
        "0%": { opacity: 0, transform: "translateY(20px)" },
        "100%": { opacity: 1, transform: "translateY(0)" },
      },
    },
  },

  

  },
  plugins: [],
}

