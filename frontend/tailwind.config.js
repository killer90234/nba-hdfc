/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        hdfc: {
          blue: '#004B8D',
          darkblue: '#003366',
          red: '#ED1C24',
          lightblue: '#E8F4FD',
          gold: '#C5A23E',
          gray: '#F5F5F5',
        },
      },
    },
  },
  plugins: [],
};
