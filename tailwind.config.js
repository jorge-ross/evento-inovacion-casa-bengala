/** @type {import('tailwindcss').Config} */
export default {
  content: [
    // Asegura que Tailwind escanee todos tus archivos React en la carpeta src/
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // Puedes añadir aquí colores, fuentes o utilidades personalizadas
    },
  },
  plugins: [],
};
