// keep your original onload + console log
window.onload = function() {
    console.log("document loaded");
    // initialize nav after window load
    initNav();
};

// close message
function dismissMessage(btn) {
    const msgEl = btn.closest('.message'); // climbs up through its(btn) ancestors - closest() vs parentElement
    msgEl.classList.add('fade-out');
    // After transition, remove from DOM
    msgEl.addEventListener('transitionend', () => {
        msgEl.remove();
    }, { once: true });
}


function initNav() {
    const toggleBtn = document.getElementById('nav-toggle');
    const menu = document.getElementById('nav-menu');
    const openIcon = document.getElementById('nav-open-icon');
    const closeIcon = document.getElementById('nav-close-icon');

    // If nav elements are not present on the page, stop silently
    if (!toggleBtn || !menu) return;

    function setAria(open) {
        toggleBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    }
    function openMenu() {
        menu.classList.remove('hidden');
        menu.classList.add('flex');
        if (openIcon) openIcon.classList.add('hidden');
        if (closeIcon) closeIcon.classList.remove('hidden');
        setAria(true);
    }
    function closeMenu() {
        menu.classList.add('hidden');
        menu.classList.remove('flex');
        if (openIcon) openIcon.classList.remove('hidden');
        if (closeIcon) closeIcon.classList.add('hidden');
        setAria(false);
    }

    toggleBtn.addEventListener('click', function () {
        const isHidden = menu.classList.contains('hidden');
        if (isHidden) openMenu();
        else closeMenu();
    });

    // close menu when any link inside menu is clicked (mobile)
    menu.addEventListener('click', function (e) {
        const target = e.target;
        if (target.tagName === 'A' || target.tagName === 'BUTTON' || target.closest('form')) {
            // only close on small screens
            if (window.innerWidth < 768) closeMenu();
        }
    });

    // responsive resize handling
    window.addEventListener('resize', function() {
        if (window.innerWidth >= 768) {
            menu.classList.remove('hidden');
            menu.classList.add('flex');
            if (openIcon) openIcon.classList.remove('hidden');
            if (closeIcon) closeIcon.classList.add('hidden');
            setAria(false);
        } else {
            const expanded = toggleBtn.getAttribute('aria-expanded') === 'true';
            if (!expanded) {
                menu.classList.add('hidden');
                menu.classList.remove('flex');
            }
        }
    });

    // initial state
    if (window.innerWidth >= 768) {
        menu.classList.remove('hidden');
        menu.classList.add('flex');
    } else {
        menu.classList.add('hidden');
        menu.classList.remove('flex');
    }
}
