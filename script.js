// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  });
});

// Mobile menu toggle (for future mobile implementation)
function toggleMobileMenu() {
  // This function can be expanded when adding a mobile hamburger menu
  console.log('Mobile menu toggle');
}

// Add scroll effect to navigation
window.addEventListener('scroll', function() {
  const nav = document.querySelector('.nav');
  if (window.scrollY > 50) {
    nav.style.background = 'rgba(255, 255, 255, 0.95)';
    nav.style.backdropFilter = 'blur(10px)';
  } else {
    nav.style.background = '#fff';
    nav.style.backdropFilter = 'none';
  }
});

// Add animation to cards on scroll
function animateOnScroll() {
  const cards = document.querySelectorAll('.feature-card, .step, .testimonial, .pricing-card');
  
  cards.forEach(card => {
    const cardTop = card.getBoundingClientRect().top;
    const windowHeight = window.innerHeight;
    
    if (cardTop < windowHeight * 0.8) {
      card.style.opacity = '1';
      card.style.transform = 'translateY(0)';
    }
  });
}

// Initialize card animations
window.addEventListener('scroll', animateOnScroll);
window.addEventListener('load', animateOnScroll);

// Add hover effects to pricing cards
document.querySelectorAll('.pricing-card').forEach(card => {
  card.addEventListener('mouseenter', function() {
    this.style.transform = 'translateY(-5px)';
  });
  
  card.addEventListener('mouseleave', function() {
    this.style.transform = 'translateY(0)';
  });
});

// Form validation (basic example)
function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

// Add click tracking for buttons (placeholder for analytics)
document.querySelectorAll('.btn').forEach(button => {
  button.addEventListener('click', function() {
    const buttonText = this.textContent.trim();
    console.log(`Button clicked: ${buttonText}`);
    // Here you could add analytics tracking
  });
});
        