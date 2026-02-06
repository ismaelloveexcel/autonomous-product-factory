# Landing Page

## 🎯 Purpose

Product landing page for Autonomous Product Factory.

## 📁 Files

- `index.html` - Main landing page (static HTML/CSS)

## 🚀 Deployment

### Option 1: Vercel (Recommended)

```bash
cd landing_page
vercel --prod
```

Your page will be live at: `https://autonomous-factory.vercel.app`

### Option 2: Netlify

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
cd landing_page
netlify deploy --prod
```

### Option 3: GitHub Pages

```bash
# Push to gh-pages branch
git subtree push --prefix landing_page origin gh-pages
```

Your page will be at: `https://yourusername.github.io/autonomous-product-factory`

### Option 4: Custom Domain

1. Deploy to any platform above
2. Point your domain DNS to the deployment
3. Configure SSL certificate

## 🎨 Customization

Edit `index.html` to customize:

- **Stats**: Update numbers in `.stats-grid`
- **Features**: Add/remove feature cards
- **Pricing**: Adjust plans in `.pricing-grid`
- **Colors**: Modify gradient in `.hero` and `.cta-section`

## 📊 Analytics

Add Google Analytics:

```html
<!-- Add before </head> -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

## 🔗 Integration

Link landing page to dashboard:

```html
<!-- Update CTA buttons -->
<a href="https://dashboard.autonomous-factory.com" class="cta-button">Try Demo</a>
```

## ✨ Features

- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Fast loading (<1s)
- ✅ SEO optimized
- ✅ Accessible (WCAG AA)
- ✅ No JavaScript required (static HTML/CSS)
- ✅ Clean, minimal design (per UI_EXCELLENCE_STANDARD)
