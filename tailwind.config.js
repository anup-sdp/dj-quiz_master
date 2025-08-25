/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './templates/**/*.html',
    './*/templates/**/*.html',
    './static/js/**/*.js',
	'./**/forms.py',
	'./**/admin.py', 
	'./**/navigation_tags.py'
	// Add others only if you actually use CSS classes in them
  ],
  plugins: [
    require('daisyui'),
  ],
  daisyui: {
    themes: ["light", "dark", "cupcake"],
  },
}
