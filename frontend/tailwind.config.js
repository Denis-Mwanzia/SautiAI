/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Kenya Flag Colors - Creative Implementation
        primary: {
          // Black (from flag) - Primary actions, headers
          50: '#f5f5f5',
          100: '#e5e5e5',
          200: '#cccccc',
          300: '#999999',
          400: '#666666',
          500: '#1a1a1a',  // Soft black
          600: '#000000',  // Pure black (flag)
          700: '#0a0a0a',
          800: '#050505',
          900: '#000000',
        },
        // Red (from flag) - Accents, alerts, energy
        kenya: {
          red: {
            50: '#fee2e2',
            100: '#fecaca',
            200: '#fca5a5',
            300: '#f87171',
            400: '#ef4444',
            500: '#DE2910',  // Official Kenyan red
            600: '#B91C1C',
            700: '#991B1B',
            800: '#7F1D1D',
            900: '#5C1A1A',
          },
          // Green (from flag) - Success, growth, prosperity
          green: {
            50: '#f0fdf4',
            100: '#dcfce7',
            200: '#bbf7d0',
            300: '#86efac',
            400: '#4ade80',
            500: '#009639',  // Official Kenyan green
            600: '#006600',  // Darker green variant
            700: '#005500',
            800: '#004400',
            900: '#003300',
          },
          // White (from flag fimbriations) - Purity, peace
          white: '#FFFFFF',
        },
      },
      backgroundImage: {
        'kenya-gradient': 'linear-gradient(180deg, #000000 0%, #DE2910 50%, #009639 100%)',
        'kenya-gradient-horizontal': 'linear-gradient(90deg, #000000 0%, #DE2910 33%, #009639 66%, #FFFFFF 100%)',
        'kenya-gradient-diagonal': 'linear-gradient(135deg, #000000 0%, #DE2910 50%, #009639 100%)',
        'kenya-gradient-soft': 'linear-gradient(135deg, rgba(0,0,0,0.05) 0%, rgba(222,41,16,0.05) 50%, rgba(0,150,57,0.05) 100%)',
        'kenya-subtle': 'linear-gradient(135deg, #f5f5f5 0%, #fff5f5 50%, #f0fdf4 100%)',
        'kenya-flag-stripes': 'repeating-linear-gradient(0deg, #000000 0%, #000000 25%, #DE2910 25%, #DE2910 50%, #009639 50%, #009639 75%, #FFFFFF 75%, #FFFFFF 100%)',
      },
      boxShadow: {
        'kenya': '0 4px 14px 0 rgba(0, 0, 0, 0.15), 0 2px 4px 0 rgba(222, 41, 16, 0.1)',
        'kenya-lg': '0 10px 25px -3px rgba(0, 0, 0, 0.2), 0 4px 6px -2px rgba(222, 41, 16, 0.15)',
        'kenya-xl': '0 20px 25px -5px rgba(0, 0, 0, 0.25), 0 10px 10px -5px rgba(222, 41, 16, 0.2)',
      },
    },
  },
  plugins: [],
}

