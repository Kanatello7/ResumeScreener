document.addEventListener("DOMContentLoaded", function () {
    const postJobBtn = document.getElementById("postJobBtn");
    const uploadCVBtn = document.getElementById("uploadCVBtn");

    postJobBtn.addEventListener("click", function () {
        window.location.href = "/post-job";
    });

    uploadCVBtn.addEventListener("click", function () {
        window.location.href = "/upload-cv";
    });
});
