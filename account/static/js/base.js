document.addEventListener("DOMContentLoaded", function () {
    const menuItems = document.querySelectorAll(".menuItemlink");

    menuItems.forEach((item) => {
        item.addEventListener("click", function () {
            // Remove active class from all
            menuItems.forEach((el) => el.classList.remove("activeLink"));

            // Add active class to clicked item
            item.classList.add("activeLink");
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const menuToggle = document.getElementById("menuToggle");
    const userMenu = document.getElementById("userMenu");

    menuToggle.addEventListener("click", function () {
        userMenu.classList.toggle("show");
    });

    document.addEventListener("click", function (event) {
        if (!menuToggle.contains(event.target) && !userMenu.contains(event.target)) {
            userMenu.classList.remove("show");
        }
    });

});
