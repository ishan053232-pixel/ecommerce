/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./**/templates/**/*.html",
    "./static/**/*.js",
  ],

  theme: {
    container: {
      center: true,
      padding: "2.5rem",
      screens: {
        xl: "1400px",
      },
    },

    extend: {
      /* =====================
         KEYFRAMES
      ===================== */
      keyframes: {
        fadeUp: {
          "0%": {
            opacity: "0",
            transform: "translateY(24px)",
          },
          "100%": {
            opacity: "1",
            transform: "translateY(0)",
          },
        },

        heroReveal: {
          "0%": {
            opacity: "0",
            transform: "translateY(40px)",
          },
          "100%": {
            opacity: "1",
            transform: "translateY(0)",
          },
        },
      },

      /* =====================
         ANIMATIONS
      ===================== */
      animation: {
        "fade-up": "fadeUp 0.9s ease-out forwards",

        /* Hero text animations */
        "hero-tag": "heroReveal 0.8s cubic-bezier(0.4,0,0.2,1) forwards",
        "hero-title": "heroReveal 1s cubic-bezier(0.4,0,0.2,1) forwards",
        "hero-desc": "heroReveal 1.2s cubic-bezier(0.4,0,0.2,1) forwards",
      },

      /* =====================
         DELAYS
      ===================== */
      transitionDelay: {
        100: "100ms",
        200: "200ms",
        300: "300ms",
        400: "400ms",
        600: "600ms",
      },
    },
  },

  plugins: [],
};
