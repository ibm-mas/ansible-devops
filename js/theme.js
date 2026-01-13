/**
 * Carbon Design System Theme for MkDocs
 * Enhanced JavaScript functionality for modern layout
 */

(function() {
    'use strict';

    // ========================================================================
    // Navigation State Management
    // ========================================================================

    /**
     * Save navigation state to localStorage
     */
    function saveNavState() {
        const expandedItems = [];
        document.querySelectorAll('cds-side-nav-menu[expanded]').forEach(menu => {
            const title = menu.getAttribute('title');
            if (title) {
                expandedItems.push(title);
            }
        });
        localStorage.setItem('mkdocs-carbon-nav-state', JSON.stringify(expandedItems));
    }

    /**
     * Load navigation state from localStorage
     */
    function loadNavState() {
        try {
            const savedState = localStorage.getItem('mkdocs-carbon-nav-state');
            if (savedState) {
                const expandedItems = JSON.parse(savedState);
                expandedItems.forEach(title => {
                    const menu = document.querySelector(`cds-side-nav-menu[title="${title}"]`);
                    if (menu) {
                        menu.setAttribute('expanded', '');
                    }
                });
            }
        } catch (e) {
            console.warn('Failed to load navigation state:', e);
        }
    }

    /**
     * Initialize navigation state persistence
     */
    function initNavStatePersistence() {
        // Load saved state on page load
        loadNavState();

        // Save state when navigation items are toggled
        document.addEventListener('click', function(e) {
            const navMenu = e.target.closest('cds-side-nav-menu');
            if (navMenu) {
                // Delay to allow the expanded attribute to update
                setTimeout(saveNavState, 100);
            }
        });
    }

    // ========================================================================
    // Table of Contents - Scroll Spy
    // ========================================================================

    /**
     * Update active TOC link based on scroll position
     */
    function updateActiveTOC() {
        const tocLinks = document.querySelectorAll('.md-toc__link');
        if (tocLinks.length === 0) return;

        const headings = Array.from(document.querySelectorAll('.rst-content h1, .rst-content h2, .rst-content h3, .rst-content h4'))
            .filter(h => h.id);

        if (headings.length === 0) return;

        // Find the current heading based on scroll position
        let currentHeading = null;
        const scrollPosition = window.scrollY + 100; // Offset for header

        for (let i = headings.length - 1; i >= 0; i--) {
            if (headings[i].offsetTop <= scrollPosition) {
                currentHeading = headings[i];
                break;
            }
        }

        // Update active state
        tocLinks.forEach(link => {
            link.classList.remove('active');
            if (currentHeading && link.getAttribute('href') === '#' + currentHeading.id) {
                link.classList.add('active');

                // Scroll TOC to keep active item visible
                const tocSidebar = document.querySelector('.md-sidebar--secondary .md-sidebar__scrollwrap');
                if (tocSidebar) {
                    const linkRect = link.getBoundingClientRect();
                    const sidebarRect = tocSidebar.getBoundingClientRect();

                    if (linkRect.top < sidebarRect.top || linkRect.bottom > sidebarRect.bottom) {
                        link.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }
                }
            }
        });
    }

    /**
     * Initialize TOC scroll spy
     */
    function initTOCScrollSpy() {
        if (document.querySelector('.md-toc')) {
            let ticking = false;

            window.addEventListener('scroll', function() {
                if (!ticking) {
                    window.requestAnimationFrame(function() {
                        updateActiveTOC();
                        ticking = false;
                    });
                    ticking = true;
                }
            });

            // Initial update
            updateActiveTOC();
        }
    }

    /**
     * Smooth scroll to anchor
     */
    function initSmoothScroll() {
        document.addEventListener('click', function(e) {
            const link = e.target.closest('a[href^="#"]');
            if (link && link.getAttribute('href') !== '#') {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                const target = document.getElementById(targetId);

                if (target) {
                    const headerOffset = 60;
                    const elementPosition = target.getBoundingClientRect().top;
                    const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                    window.scrollTo({
                        top: offsetPosition,
                        behavior: 'smooth'
                    });

                    // Update URL without jumping
                    history.pushState(null, null, '#' + targetId);
                }
            }
        });
    }

    // ========================================================================
    // Mobile Menu Toggle
    // ========================================================================

    /**
     * Toggle mobile navigation
     */
    function initMobileMenu() {
        const menuButton = document.querySelector('cds-header-menu-button');
        const sidebar = document.querySelector('.md-sidebar--primary');

        if (menuButton && sidebar) {
            menuButton.addEventListener('click', function() {
                sidebar.classList.toggle('active');

                // Close menu when clicking outside
                if (sidebar.classList.contains('active')) {
                    document.addEventListener('click', closeMobileMenuOnClickOutside);
                }
            });
        }
    }

    /**
     * Close mobile menu when clicking outside
     */
    function closeMobileMenuOnClickOutside(e) {
        const sidebar = document.querySelector('.md-sidebar--primary');
        const menuButton = document.querySelector('cds-header-menu-button');

        if (sidebar &&
            !sidebar.contains(e.target) &&
            !menuButton.contains(e.target)) {
            sidebar.classList.remove('active');
            document.removeEventListener('click', closeMobileMenuOnClickOutside);
        }
    }

    /**
     * Close mobile menu on navigation
     */
    function closeMobileMenuOnNav() {
        document.addEventListener('click', function(e) {
            const navLink = e.target.closest('.md-sidebar--primary a');
            if (navLink && window.innerWidth < 768) {
                const sidebar = document.querySelector('.md-sidebar--primary');
                if (sidebar) {
                    sidebar.classList.remove('active');
                }
            }
        });
    }

    // ========================================================================
    // Keyboard Shortcuts
    // ========================================================================

    /**
     * Initialize keyboard shortcuts
     */
    function initKeyboardShortcuts() {
        document.addEventListener('keydown', function(e) {
            // Focus search on '/' key
            if (e.key === '/' && !e.ctrlKey && !e.metaKey && !e.altKey) {
                const searchInput = document.querySelector('#header-search');
                if (searchInput &&
                    document.activeElement.tagName !== 'INPUT' &&
                    document.activeElement.tagName !== 'TEXTAREA') {
                    e.preventDefault();
                    searchInput.click();
                }
            }
        });
    }

    // ========================================================================
    // Legacy Functions (for backward compatibility)
    // ========================================================================

    /**
     * Used by the Select in the breadcrumbs (legacy)
     */
    window.changeAnchor = function(val) {
        if (val) {
            window.location.hash = val;
        }
    };

    // ========================================================================
    // Back to Top Button
    // ========================================================================

    /**
     * Create and manage back to top button
     */
    function initBackToTop() {
        // Create button
        const button = document.createElement('button');
        button.className = 'md-back-to-top';
        button.setAttribute('aria-label', 'Back to top');
        button.innerHTML = `
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M7.41 15.41L12 10.83l4.59 4.58L18 14l-6-6-6 6z"/>
            </svg>
        `;
        document.body.appendChild(button);

        // Show/hide based on scroll position
        let ticking = false;
        window.addEventListener('scroll', function() {
            if (!ticking) {
                window.requestAnimationFrame(function() {
                    if (window.scrollY > 300) {
                        button.classList.add('visible');
                    } else {
                        button.classList.remove('visible');
                    }
                    ticking = false;
                });
                ticking = true;
            }
        });

        // Scroll to top on click
        button.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // ========================================================================
    // Theme Toggle
    // ========================================================================

    /**
     * Initialize theme toggle functionality
     */
    function initThemeToggle() {
        const toggleButton = document.querySelector('.md-theme-toggle__button');
        const toggleMenu = document.querySelector('.md-theme-toggle__menu');
        const themeOptions = document.querySelectorAll('.md-theme-toggle__option');

        // Get default theme from body data attribute, fallback to g90 (Dark Gray)
        const defaultTheme = document.body.getAttribute('data-theme-default') || 'g90';

        // Load saved theme preference, or use configured default
        const savedTheme = localStorage.getItem('mkdocs-carbon-theme') || defaultTheme;

        // Apply theme immediately (even if toggle is disabled)
        applyTheme(savedTheme);

        if (!toggleButton || !toggleMenu) return;

        // Apply theme immediately
        applyTheme(savedTheme);
        updateActiveTheme(savedTheme);

        // Also apply on page load to ensure all components are themed
        setTimeout(function() {
            applyTheme(savedTheme);
        }, 100);

        // Toggle menu visibility
        toggleButton.addEventListener('click', function(e) {
            e.stopPropagation();
            const isHidden = toggleMenu.hasAttribute('hidden');
            if (isHidden) {
                toggleMenu.removeAttribute('hidden');
            } else {
                toggleMenu.setAttribute('hidden', '');
            }
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!toggleMenu.contains(e.target) && !toggleButton.contains(e.target)) {
                toggleMenu.setAttribute('hidden', '');
            }
        });

        // Handle theme selection
        themeOptions.forEach(function(option) {
            option.addEventListener('click', function() {
                const theme = this.getAttribute('data-theme');
                applyTheme(theme);
                updateActiveTheme(theme);
                localStorage.setItem('mkdocs-carbon-theme', theme);
                toggleMenu.setAttribute('hidden', '');
            });
        });
    }

    /**
     * Apply theme to page elements
     */
    function applyTheme(theme) {
        // Apply to body for CSS variable inheritance
        document.body.setAttribute('data-carbon-theme', theme);

        // Apply to sidebars
        const sideNav = document.querySelector('cds-side-nav');
        if (sideNav) {
            sideNav.className = `cds-theme-zone-${theme}`;
        }

        // Apply to header if different theme is configured
        const header = document.querySelector('cds-header');
        if (header && !header.classList.contains('cds-theme-zone-g100')) {
            // Only change header theme if it's not explicitly set to g100
            header.className = header.className.replace(/cds-theme-zone-\w+/, `cds-theme-zone-${theme}`);
        }

        // Apply to all tabs components
        const tabs = document.querySelectorAll('cds-tabs');
        tabs.forEach(function(tab) {
            tab.className = `cds-theme-zone-${theme}`;
        });

        // Apply to all accordion components
        const accordions = document.querySelectorAll('cds-accordion');
        accordions.forEach(function(accordion) {
            accordion.className = `cds-theme-zone-${theme}`;
        });

        // Re-apply accordion title styling after theme change
        setTimeout(styleAccordionTitles, 100);

        // Switch HighlightJS theme based on Carbon theme
        const hljsLight = document.getElementById('hljs-light');
        const hljsDark = document.getElementById('hljs-dark');
        if (hljsLight && hljsDark) {
            if (theme === 'g90' || theme === 'g100') {
                hljsLight.disabled = true;
                hljsDark.disabled = false;
            } else {
                hljsLight.disabled = false;
                hljsDark.disabled = true;
            }
        }

        // Update content area background
        const content = document.querySelector('.md-content');
        if (content) {
            if (theme === 'g90' || theme === 'g100') {
                content.style.backgroundColor = 'var(--background)';
                content.style.color = 'var(--text-primary)';
            } else {
                content.style.backgroundColor = '';
                content.style.color = '';
            }
        }
    }

    /**
     * Update active theme indicator
     */
    function updateActiveTheme(theme) {
        const options = document.querySelectorAll('.md-theme-toggle__option');
        options.forEach(function(option) {
            if (option.getAttribute('data-theme') === theme) {
                option.classList.add('active');
            } else {
                option.classList.remove('active');
            }
        });
    }

    // ========================================================================
    // Copy to Clipboard for Code Blocks
    // ========================================================================

    /**
     * Add copy buttons to code blocks
     */
    function initCopyButtons() {
        const codeBlocks = document.querySelectorAll('.rst-content pre code');

        codeBlocks.forEach(function(codeBlock) {
            const pre = codeBlock.parentElement;
            if (!pre.querySelector('.md-code-copy')) {
                const button = document.createElement('button');
                button.className = 'md-code-copy';
                button.setAttribute('aria-label', 'Copy to clipboard');
                button.innerHTML = `
                    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
                    </svg>
                `;

                button.addEventListener('click', function() {
                    const code = codeBlock.textContent;
                    navigator.clipboard.writeText(code).then(function() {
                        button.classList.add('copied');
                        button.innerHTML = `
                            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                            </svg>
                        `;
                        setTimeout(function() {
                            button.classList.remove('copied');
                            button.innerHTML = `
                                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
                                </svg>
                            `;
                        }, 2000);
                    }).catch(function(err) {
                        console.error('Failed to copy:', err);
                    });
                });

                pre.style.position = 'relative';
                pre.appendChild(button);
            }
        });
    }

    // ========================================================================
    // Accordion Styling
    // ========================================================================

    /**
     * Style accordion titles to be bold by accessing Shadow DOM
     */
    function styleAccordionTitles() {
        const accordions = document.querySelectorAll('cds-accordion-item');
        accordions.forEach(function(accordion) {
            // Access shadow root and style the title
            if (accordion.shadowRoot) {
                const titleElement = accordion.shadowRoot.querySelector('.cds--accordion__heading');
                if (titleElement) {
                    titleElement.style.fontWeight = '600';
                    titleElement.style.fontSize = '1rem';
                }

                // Also try the button element
                const button = accordion.shadowRoot.querySelector('.cds--accordion__button');
                if (button) {
                    button.style.fontWeight = '600';
                }

                // Try the title text wrapper
                const titleText = accordion.shadowRoot.querySelector('.cds--accordion__title');
                if (titleText) {
                    titleText.style.fontWeight = '600';
                }
            }
        });
    }

    // ========================================================================
    // Initialization
    // ========================================================================

    /**
     * Initialize all functionality when DOM is ready
     */
    function init() {
        // Wait for Carbon components to be ready
        if (customElements.get('cds-side-nav')) {
            initNavStatePersistence();
            initTOCScrollSpy();
            initSmoothScroll();
            initMobileMenu();
            closeMobileMenuOnNav();
            initKeyboardShortcuts();
            initBackToTop();
            initThemeToggle();
            initCopyButtons();

            // Style accordion titles after a delay to ensure they're fully rendered
            setTimeout(styleAccordionTitles, 200);
            // Also re-apply when theme changes
            setTimeout(styleAccordionTitles, 500);
        } else {
            // Retry after a short delay if components aren't ready
            setTimeout(init, 100);
        }
    }

    // Start initialization when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();

// Made with Bob
