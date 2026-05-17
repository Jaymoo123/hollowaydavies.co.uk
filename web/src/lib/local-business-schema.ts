/**
 * Local Business JSON-LD Schema Generator
 * For location-specific landing pages
 */

interface LocalBusinessConfig {
  name: string;
  legalName: string;
  description: string;
  url: string;
  logo: string;
  email: string;
  phone: string;
  areaServed: string;
  city: string;
  organizationType: string;
}

export function buildLocalBusinessJsonLd(config: LocalBusinessConfig): string {
  const schema = {
    "@context": "https://schema.org",
    "@type": config.organizationType,
    "name": `${config.name} - ${config.city}`,
    "legalName": config.legalName,
    "description": config.description,
    "url": config.url,
    "logo": config.logo,
    "image": config.logo,
    "address": {
      "@type": "PostalAddress",
      "addressLocality": config.city,
      "addressCountry": "GB"
    },
    "areaServed": {
      "@type": "City",
      "name": config.city,
      "containedInPlace": {
        "@type": "Country",
        "name": "United Kingdom"
      }
    },
    "contactPoint": {
      "@type": "ContactPoint",
      "telephone": config.phone,
      "email": config.email,
      "contactType": "customer service",
      "areaServed": "GB",
      "availableLanguage": ["English"]
    },
    "priceRange": "££",
    "openingHoursSpecification": {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday"
      ],
      "opens": "09:00",
      "closes": "17:00"
    }
  };

  return JSON.stringify(schema);
}
