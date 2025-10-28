document.addEventListener('DOMContentLoaded', () => {
    const menuToggle = document.querySelector('.menu-toggle');
    const navMenu = document.querySelector('.nav-menu');

    // Toggle Mobile Navigation Menu
    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active'); 
        });
    }

    // --- New: Number Counting Animation ---
    const stats = [
        { selector: '.stat-card:nth-child(1) span', endValue: 2, duration: 1000, prefix: '' },
        { selector: '.stat-card:nth-child(2) span', endValue: 9500, duration: 2000, prefix: '$' },
        { selector: '.stat-card:nth-child(3) span', endValue: 6500, duration: 2000, prefix: '$' }
    ];

    const animateCount = (element, endValue, duration, prefix) => {
        let startValue = 0;
        const startTime = performance.now();

        const step = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const currentValue = Math.floor(progress * endValue);

            element.textContent = prefix + currentValue.toLocaleString();

            if (progress < 1) {
                requestAnimationFrame(step);
            } else {
                element.textContent = prefix + endValue.toLocaleString(); // Ensure final value is accurate
            }
        };

        requestAnimationFrame(step);
    };

    const dashboardPreview = document.querySelector('.dashboard-preview');
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1 // Trigger when 10% of the element is visible
    };
    
    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                stats.forEach(stat => {
                    const element = document.querySelector(stat.selector);
                    if (element) {
                        animateCount(element, stat.endValue, stat.duration, stat.prefix);
                    }
                });
                observer.unobserve(entry.target); // Stop observing once the animation runs
            }
        });
    }, observerOptions);

    if (dashboardPreview) {
        observer.observe(dashboardPreview);
    }
    // --- End: Number Counting Animation ---
});