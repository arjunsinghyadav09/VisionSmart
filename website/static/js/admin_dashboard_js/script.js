document.addEventListener("DOMContentLoaded", function () {
    const parentMenuItems = document.querySelectorAll(".sidebar-menu li");

    parentMenuItems.forEach((menuItem) => {
        menuItem.addEventListener("click", function () {
            const subMenu = this.querySelector("ul");
            if (subMenu) {
                subMenu.classList.toggle("active");
            }
        });
    });
});
