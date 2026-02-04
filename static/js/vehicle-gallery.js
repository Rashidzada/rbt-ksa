(function () {
    const galleryRoots = document.querySelectorAll('[data-vehicle-gallery]');
    if (!galleryRoots.length) {
        return;
    }

    const FALLBACK_IMAGE = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 900'%3E%3Crect width='1200' height='900' fill='%23e5e7eb'/%3E%3Cg fill='%236b7280'%3E%3Cpath d='M357 327h486v246H357z' opacity='.22'/%3E%3Cpath d='M477 498l90-108 120 156 78-90 111 144H324z'/%3E%3Ccircle cx='459' cy='429' r='42'/%3E%3C/g%3E%3Ctext x='600' y='654' font-family='Arial, sans-serif' font-size='56' fill='%236b7280' text-anchor='middle'%3EImage unavailable%3C/text%3E%3C/svg%3E";
    let modalLocks = 0;

    const lockBodyScroll = function () {
        if (modalLocks === 0) {
            document.body.style.overflow = 'hidden';
        }
        modalLocks += 1;
    };

    const unlockBodyScroll = function () {
        modalLocks = Math.max(0, modalLocks - 1);
        if (modalLocks === 0) {
            document.body.style.overflow = '';
        }
    };

    const normalizeIndex = function (index, total) {
        if (total <= 0) {
            return 0;
        }
        return ((index % total) + total) % total;
    };

    const attachImageLifecycle = function (image) {
        if (!image || image.dataset.galleryLifecycleBound === '1') {
            return;
        }
        image.dataset.galleryLifecycleBound = '1';
        image.addEventListener('load', function () {
            image.classList.remove('is-loading');
        });
        image.addEventListener('error', function () {
            if (image.dataset.galleryFallbackApplied === '1') {
                image.classList.remove('is-loading');
                return;
            }
            image.dataset.galleryFallbackApplied = '1';
            image.src = FALLBACK_IMAGE;
            image.classList.remove('is-loading');
        });
    };

    const setImage = function (image, src, altText) {
        if (!image) {
            return;
        }
        image.dataset.galleryFallbackApplied = '0';
        image.classList.add('is-loading');
        image.alt = altText || 'Vehicle image';
        image.src = src || FALLBACK_IMAGE;
    };

    const attachSwipe = function (element, onSwipeRight, onSwipeLeft) {
        if (!element) {
            return;
        }
        let startX = 0;
        let startY = 0;
        let pointerId = null;

        element.addEventListener('pointerdown', function (event) {
            if (event.pointerType === 'mouse' && event.button !== 0) {
                return;
            }
            pointerId = event.pointerId;
            startX = event.clientX;
            startY = event.clientY;
        });

        element.addEventListener('pointerup', function (event) {
            if (pointerId === null || event.pointerId !== pointerId) {
                return;
            }
            const deltaX = event.clientX - startX;
            const deltaY = event.clientY - startY;
            pointerId = null;

            if (Math.abs(deltaX) < 44 || Math.abs(deltaX) <= Math.abs(deltaY)) {
                return;
            }
            if (deltaX < 0) {
                onSwipeLeft();
            } else {
                onSwipeRight();
            }
        });

        element.addEventListener('pointercancel', function () {
            pointerId = null;
        });
    };

    galleryRoots.forEach(function (galleryRoot) {
        const wrapper = galleryRoot.closest('.vehicle-gallery') || galleryRoot;
        const stage = galleryRoot.querySelector('.vehicle-gallery-stage');
        const mainButton = galleryRoot.querySelector('[data-gallery-main-button]');
        const mainImage = galleryRoot.querySelector('[data-gallery-main-image]');
        const thumbsTrack = galleryRoot.querySelector('[data-gallery-thumbs]');
        const thumbButtons = Array.from(galleryRoot.querySelectorAll('[data-gallery-thumb]'));
        const placeholder = galleryRoot.querySelector('[data-gallery-placeholder]');
        const counter = galleryRoot.querySelector('[data-gallery-counter]');

        const modal = wrapper.querySelector('[data-gallery-modal]');
        const modalStage = wrapper.querySelector('[data-gallery-modal-stage]');
        const modalImage = wrapper.querySelector('[data-gallery-modal-image]');
        const modalCounter = wrapper.querySelector('[data-gallery-modal-counter]');
        const modalClose = wrapper.querySelector('[data-gallery-close]');

        const prevButtons = Array.from(wrapper.querySelectorAll('[data-gallery-prev]'));
        const nextButtons = Array.from(wrapper.querySelectorAll('[data-gallery-next]'));

        const slides = thumbButtons.map(function (button, index) {
            const src = button.dataset.gallerySrc || '';
            const alt = button.dataset.galleryAlt || ('Vehicle image ' + (index + 1));
            return { button: button, src: src, alt: alt };
        }).filter(function (item) {
            return Boolean(item.src);
        });

        if (mainImage) {
            attachImageLifecycle(mainImage);
        }
        if (modalImage) {
            attachImageLifecycle(modalImage);
        }

        thumbButtons.forEach(function (button) {
            const image = button.querySelector('img');
            if (image) {
                attachImageLifecycle(image);
            }
        });

        if (!slides.length) {
            if (placeholder) {
                placeholder.classList.remove('hidden');
                placeholder.classList.add('flex');
            }
            if (mainImage) {
                mainImage.classList.add('hidden');
            }
            if (mainButton) {
                mainButton.disabled = true;
                mainButton.setAttribute('aria-disabled', 'true');
            }
            if (thumbsTrack) {
                thumbsTrack.classList.add('hidden');
            }
            if (counter) {
                counter.textContent = '0 / 0';
            }
            prevButtons.forEach(function (button) {
                button.classList.add('hidden');
            });
            nextButtons.forEach(function (button) {
                button.classList.add('hidden');
            });
            return;
        }

        if (slides.length < 2) {
            prevButtons.forEach(function (button) {
                button.classList.add('hidden');
            });
            nextButtons.forEach(function (button) {
                button.classList.add('hidden');
            });
        }

        let currentIndex = 0;
        let isModalOpen = false;
        let previousFocus = null;
        let suppressMainClick = false;
        let suppressMainClickTimer = null;

        const markSwipeNavigation = function () {
            suppressMainClick = true;
            if (suppressMainClickTimer) {
                window.clearTimeout(suppressMainClickTimer);
            }
            suppressMainClickTimer = window.setTimeout(function () {
                suppressMainClick = false;
                suppressMainClickTimer = null;
            }, 260);
        };

        const setCounters = function () {
            const label = (currentIndex + 1) + ' / ' + slides.length;
            if (counter) {
                counter.textContent = label;
            }
            if (modalCounter) {
                modalCounter.textContent = label;
            }
        };

        const setActiveThumb = function (scrollIntoView) {
            slides.forEach(function (slide, index) {
                const isActive = index === currentIndex;
                slide.button.classList.toggle('is-active', isActive);
                slide.button.setAttribute('aria-current', isActive ? 'true' : 'false');
            });

            if (scrollIntoView) {
                const currentThumb = slides[currentIndex] && slides[currentIndex].button;
                if (currentThumb) {
                    currentThumb.scrollIntoView({
                        behavior: 'smooth',
                        block: 'nearest',
                        inline: 'center'
                    });
                }
            }
        };

        const renderCurrentImage = function (scrollIntoView) {
            const currentSlide = slides[currentIndex];
            setImage(mainImage, currentSlide.src, currentSlide.alt);
            setImage(modalImage, currentSlide.src, currentSlide.alt);
            if (mainImage) {
                mainImage.classList.remove('hidden');
            }
            if (placeholder) {
                placeholder.classList.add('hidden');
                placeholder.classList.remove('flex');
            }
            setActiveThumb(scrollIntoView);
            setCounters();
        };

        const showAt = function (index, scrollIntoView) {
            currentIndex = normalizeIndex(index, slides.length);
            renderCurrentImage(scrollIntoView !== false);
        };

        const showPrevious = function () {
            showAt(currentIndex - 1, true);
        };

        const showNext = function () {
            showAt(currentIndex + 1, true);
        };

        const openModal = function () {
            if (!modal || isModalOpen) {
                return;
            }
            previousFocus = document.activeElement instanceof HTMLElement ? document.activeElement : null;
            modal.hidden = false;
            isModalOpen = true;
            lockBodyScroll();
            window.setTimeout(function () {
                if (modalClose) {
                    modalClose.focus();
                }
            }, 0);
        };

        const closeModal = function () {
            if (!modal || !isModalOpen) {
                return;
            }
            modal.hidden = true;
            isModalOpen = false;
            unlockBodyScroll();
            if (previousFocus && typeof previousFocus.focus === 'function') {
                previousFocus.focus();
            }
        };

        slides.forEach(function (slide, index) {
            slide.button.addEventListener('click', function () {
                showAt(index, false);
            });
            slide.button.addEventListener('keydown', function (event) {
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    showAt(index, false);
                }
            });
        });

        prevButtons.forEach(function (button) {
            button.addEventListener('click', function (event) {
                event.stopPropagation();
                showPrevious();
            });
        });

        nextButtons.forEach(function (button) {
            button.addEventListener('click', function (event) {
                event.stopPropagation();
                showNext();
            });
        });

        if (mainButton) {
            mainButton.addEventListener('click', function () {
                if (suppressMainClick) {
                    suppressMainClick = false;
                    return;
                }
                if (slides.length) {
                    openModal();
                }
            });
            mainButton.addEventListener('keydown', function (event) {
                if (event.key === 'ArrowLeft') {
                    event.preventDefault();
                    showPrevious();
                } else if (event.key === 'ArrowRight') {
                    event.preventDefault();
                    showNext();
                } else if ((event.key === 'Enter' || event.key === ' ') && slides.length) {
                    event.preventDefault();
                    openModal();
                }
            });
        }

        if (modalClose) {
            modalClose.addEventListener('click', function () {
                closeModal();
            });
        }

        if (modal) {
            modal.addEventListener('click', function (event) {
                if (event.target === modal) {
                    closeModal();
                }
            });
        }

        document.addEventListener('keydown', function (event) {
            if (isModalOpen) {
                if (event.key === 'Escape') {
                    event.preventDefault();
                    closeModal();
                } else if (event.key === 'ArrowLeft') {
                    event.preventDefault();
                    showPrevious();
                } else if (event.key === 'ArrowRight') {
                    event.preventDefault();
                    showNext();
                }
                return;
            }

            const focusedElement = document.activeElement;
            const isInGallery = focusedElement instanceof HTMLElement && wrapper.contains(focusedElement);
            if (!isInGallery) {
                return;
            }
            if (event.key === 'ArrowLeft') {
                event.preventDefault();
                showPrevious();
            } else if (event.key === 'ArrowRight') {
                event.preventDefault();
                showNext();
            }
        });

        attachSwipe(stage, function () {
            markSwipeNavigation();
            showPrevious();
        }, function () {
            markSwipeNavigation();
            showNext();
        });
        attachSwipe(modalStage, showPrevious, showNext);
        showAt(0, false);
    });
})();
