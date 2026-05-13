/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./node_modules/flowbite-react/**/*.{js,jsx,ts,tsx}",
    "./node_modules/flowbite/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        liga: {
          green: "#1a7a3c",
          "green-dark": "#145f2e",
          "green-light": "#22a44f",
          gold: "#f5a623",
          dark: "#0f172a",
        },
      },
    },
  },
  plugins: [require("flowbite/plugin")],
};
