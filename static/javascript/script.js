window.onload = function() {
    console.log("document loaded");
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