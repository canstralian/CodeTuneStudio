/**
 * Structured Data (JSON-LD) for CodeTune Studio Lite
 * 
 * This file contains the JSON-LD structured data for search engine optimization.
 * Separated from HTML for easier management and maintenance.
 */

const structuredData = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "CodeTune Studio Lite",
  "applicationCategory": "DeveloperApplication",
  "description": "Boost your productivity with CodeTune Studio Lite — the AI-powered code optimizer that automatically refactors, debugs, and improves your Python, JavaScript, and Bash scripts.",
  "operatingSystem": "Web-based",
  "url": "https://codetunestudio.app",
  "offers": [
    {
      "@type": "Offer",
      "name": "Free Plan",
      "price": "0",
      "priceCurrency": "USD",
      "description": "1 AI optimization per day with limited support."
    },
    {
      "@type": "Offer",
      "name": "Developer Plan",
      "price": "10.00",
      "priceCurrency": "USD",
      "priceSpecification": {
        "@type": "PriceSpecification",
        "price": "10.00",
        "priceCurrency": "USD",
        "billingCycle": "P1M"
      },
      "description": "Unlimited AI refactors, priority queue access, and code history."
    }
  ],
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.9",
    "reviewCount": "2",
    "bestRating": "5",
    "worstRating": "1"
  },
  "review": [
    {
      "@type": "Review",
      "author": {
        "@type": "Person",
        "name": "Alex, Full Stack Developer"
      },
      "reviewRating": {
        "@type": "Rating",
        "ratingValue": "5"
      },
      "reviewBody": "I run all my Python scripts through CodeTune before production — it's like having a senior engineer review my work."
    },
    {
      "@type": "Review",
      "author": {
        "@type": "Person",
        "name": "Priya, Data Scientist"
      },
      "reviewRating": {
        "@type": "Rating",
        "ratingValue": "5"
      },
      "reviewBody": "It helped me spot performance issues I missed for months."
    }
  ],
  "potentialAction": {
    "@type": "Action",
    "name": "Try CodeTune Studio Lite for Free",
    "target": {
      "@type": "EntryPoint",
      "urlTemplate": "https://codetunestudio.app/register",
      "inLanguage": "en-US",
      "actionPlatform": [
        "http://schema.org/DesktopWebPlatform",
        "http://schema.org/IOSPlatform",
        "http://schema.org/AndroidPlatform"
      ]
    }
  }
};

// Inject the structured data into the page
(function() {
  const script = document.createElement('script');
  script.type = 'application/ld+json';
  script.textContent = JSON.stringify(structuredData);
  document.head.appendChild(script);
})();
