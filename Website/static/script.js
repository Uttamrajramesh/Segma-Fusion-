// SegmaFusion - Dashboard JavaScript

document.addEventListener("DOMContentLoaded", function () {
    console.log("SegmaFusion JavaScript loaded successfully!");

    // Handle links that are temporarily disabled
    document.querySelectorAll("[data-disabled='true']").forEach(function (element) {
        element.addEventListener("click", function (event) {
            event.preventDefault();
            alert("This feature is coming soon!");
        });
    });
});