// Main JavaScript for Premium Chauffeur Blog

document.addEventListener('DOMContentLoaded', function() {
    // Initialize page navigation
    initializePageNavigation();

    // Initialize mobile menu if exists
    initializeMobileMenu();

    // Initialize lazy loading for images
    initializeLazyLoading();

    // Initialize WebGL light rays for hero section
    initializeLightRays();
});

function initializePageNavigation() {
    const pageButtons = document.querySelectorAll('.page-btn');
    const sections = document.querySelectorAll('.blog-section');

    if (pageButtons.length === 0) return;

    pageButtons.forEach((button) => {
        button.addEventListener('click', () => {
            const targetSection = button.getAttribute('data-section');

            // Remove active class from all buttons and sections
            pageButtons.forEach(btn => btn.classList.remove('active'));
            sections.forEach(section => section.classList.remove('active'));

            // Add active class to clicked button and corresponding section
            button.classList.add('active');
            const targetElement = document.getElementById(targetSection);
            if (targetElement) {
                targetElement.classList.add('active');
            }
        });
    });

    // Show all sections by default (they already have active class in HTML)
    if (pageButtons.length > 0) {
        pageButtons[0].classList.add('active');
    }
}

function initializeMobileMenu() {
    const mobileToggle = document.getElementById('mobile-menu-toggle');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileToggle && mobileMenu) {
        mobileToggle.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }
}

function initializeLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback for browsers without IntersectionObserver
        images.forEach(img => {
            img.src = img.dataset.src;
        });
    }
}

// Smooth scrolling for anchor links
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

// Analytics tracking for blog card clicks and section tracking
document.querySelectorAll('.read-more').forEach(link => {
    link.addEventListener('click', function(e) {
        const cardTitle = this.closest('.card-content').querySelector('.card-title').textContent;

        // Find which section this card belongs to
        const section = this.closest('.blog-section');
        if (section) {
            const sectionId = section.id;
            // Store the section ID in sessionStorage so we can return to it
            sessionStorage.setItem('returnToSection', sectionId);
        }

        // Analytics tracking code would go here
        console.log('Blog card clicked:', cardTitle);
    });
});

// Search functionality
function initializeSearch() {
    const searchInput = document.getElementById('searchInput');
    const blogCards = document.querySelectorAll('.blog-card');

    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();

            blogCards.forEach(card => {
                const title = card.querySelector('h3').textContent.toLowerCase();
                const description = card.querySelector('p').textContent.toLowerCase();

                if (title.includes(searchTerm) || description.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
}

// Category filtering functionality
function initializeCategoryFiltering() {
    const categoryBtns = document.querySelectorAll('.category-btn');
    const blogSections = document.querySelectorAll('.blog-section');

    // Ensure "All" button is active by default and all sections are shown
    const allBtn = document.querySelector('.category-btn[data-category="all"]');
    if (allBtn && !allBtn.classList.contains('active')) {
        categoryBtns.forEach(btn => btn.classList.remove('active'));
        allBtn.classList.add('active');
        blogSections.forEach(section => section.classList.add('active'));
    }

    categoryBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from all buttons
            categoryBtns.forEach(b => b.classList.remove('active'));
            // Add active class to clicked button
            this.classList.add('active');

            const category = this.dataset.category;

            if (category === 'all') {
                // Show all sections
                blogSections.forEach(section => {
                    section.classList.add('active');
                });
            } else {
                // Hide all sections first
                blogSections.forEach(section => {
                    section.classList.remove('active');
                });

                // Show selected category
                const targetSection = document.getElementById(category);
                if (targetSection) {
                    targetSection.classList.add('active');
                }
            }

            // Clear search when switching categories
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                searchInput.value = '';
                // Reset all card visibility
                document.querySelectorAll('.blog-card').forEach(card => {
                    card.style.display = 'block';
                });
            }
        });
    });
}

// Initialize WebGL Light Rays
function initializeLightRays() {
    const heroSection = document.querySelector('.hero-section');
    if (!heroSection || typeof LightRays === 'undefined') {
        console.log('WebGL Light Rays not available, using CSS fallback');
        return;
    }

    // Create container for WebGL canvas
    const lightRaysContainer = document.createElement('div');
    lightRaysContainer.className = 'light-rays-webgl';
    lightRaysContainer.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 1;
    `;

    heroSection.appendChild(lightRaysContainer);

    // Initialize WebGL light rays with gold color and settings from lightrays.txt
    const lightRays = new LightRays(lightRaysContainer, {
        raysOrigin: "top-center",
        raysColor: "#ffd700", // Gold color
        raysSpeed: 1,
        lightSpread: 0.5,
        rayLength: 3,
        pulsating: false,
        fadeDistance: 1,
        saturation: 1,
        followMouse: true,
        mouseInfluence: 0.1,
        noiseAmount: 0,
        distortion: 0
    });

    // Store reference for cleanup if needed
    heroSection.lightRaysInstance = lightRays;
}

// Handle return navigation from guide pages
function handleReturnNavigation() {
    // Check if we're on the main page and have a return section stored
    const returnSection = sessionStorage.getItem('returnToSection');
    if (returnSection && window.location.pathname === '/') {
        // Clear the stored section
        sessionStorage.removeItem('returnToSection');

        // Navigate to the specific section
        const categoryBtns = document.querySelectorAll('.category-btn');
        const targetBtn = document.querySelector(`[data-category="${returnSection}"]`);

        if (targetBtn) {
            // Remove active from all buttons
            categoryBtns.forEach(btn => btn.classList.remove('active'));
            // Add active to target button
            targetBtn.classList.add('active');

            // Show only the target section
            const blogSections = document.querySelectorAll('.blog-section');
            blogSections.forEach(section => {
                section.classList.remove('active');
            });

            const targetSectionElement = document.getElementById(returnSection);
            if (targetSectionElement) {
                targetSectionElement.classList.add('active');
                // Scroll to the section
                targetSectionElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }
    }
}

// Initialize new functionality
document.addEventListener('DOMContentLoaded', function() {
    initializeSearch();
    initializeCategoryFiltering();
    handleReturnNavigation();
});
