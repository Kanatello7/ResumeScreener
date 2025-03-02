document.addEventListener("DOMContentLoaded", function () {
    const dropArea = document.getElementById("dropArea");
    const fileInput = document.getElementById("fileInput");
    const fileNameDisplay = document.getElementById("fileName");

    // Drag Over Event
    dropArea.addEventListener("dragover", function (e) {
        e.preventDefault();
        dropArea.style.backgroundColor = "#eef5ff";
    });

    // Drag Leave Event
    dropArea.addEventListener("dragleave", function () {
        dropArea.style.backgroundColor = "#f8faff";
    });

    // Drop Event
    dropArea.addEventListener("drop", function (e) {
        e.preventDefault();
        dropArea.style.backgroundColor = "#f8faff";

        if (e.dataTransfer.files.length > 0) {
            const file = e.dataTransfer.files[0];
            fileNameDisplay.textContent = "Selected file: " + file.name;
        }
    });

    // Browse File Event
    fileInput.addEventListener("change", function (e) {
        if (e.target.files.length > 0) {
            fileNameDisplay.textContent = "Selected file: " + e.target.files[0].name;
        }
    });
});
