(() => {
    const loader = document.getElementById("segma-loader");

    if (!loader) {
        return;
    }

    const message = loader.querySelector(".loader-message");
    let hideTimer;

    function showLoader(text) {
        if (message && text) {
            message.replaceChildren();

            const label = document.createElement("span");
            label.textContent = text;

            const dots = document.createElement("span");
            dots.className = "loader-dots";

            for (let i = 0; i < 3; i++) {
                const dot = document.createElement("span");
                dot.textContent = ".";
                dots.appendChild(dot);
            }

            message.append(label, dots);
        }

        clearTimeout(hideTimer);
        loader.classList.remove("loader-hidden");
        loader.setAttribute("aria-hidden", "false");
    }

    function hideLoader() {
        clearTimeout(hideTimer);

        loader.classList.add("loader-hidden");
        loader.setAttribute("aria-hidden", "true");
    }

    // Hide the loader when the page has finished loading.
    window.addEventListener("load", () => {
        hideTimer = setTimeout(hideLoader, 5000);
    });

    // Show the loader during navigation to another local page.
    document.addEventListener("click", (event) => {
        const link = event.target.closest("a");

        if (!link) {
            return;
        }

        if (
            event.defaultPrevented ||
            event.button !== 0 ||
            event.ctrlKey ||
            event.metaKey ||
            event.shiftKey ||
            event.altKey ||
            link.target === "_blank" ||
            link.hasAttribute("download")
        ) {
            return;
        }

        const destination = new URL(link.href, window.location.href);

        if (
            destination.origin !== window.location.origin ||
            destination.href === window.location.href ||
            (
                destination.hash &&
                destination.pathname === window.location.pathname
            )
        ) {
            return;
        }

        showLoader("Preparing your workspace");
    });

    // Show the loader when a valid form is submitted.
    document.addEventListener("submit", (event) => {
        const form = event.target;

        if (!(form instanceof HTMLFormElement)) {
            return;
        }

        if (!form.checkValidity()) {
            return;
        }

        showLoader("Preparing your workspace");
    });

    // Hide the loader when returning through browser navigation.
    window.addEventListener("pageshow", () => {
        hideLoader();
    });

    // Allow other scripts to control the loader.
    window.SegmaLoader = {
        show: showLoader,
        hide: hideLoader
    };
})();