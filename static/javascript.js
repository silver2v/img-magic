
const inpFile = document.getElementById("inpFile");
const previewContainer = document.getElementById("imagePreview");
const previewImage = previewContainer.querySelector(".image-preview__image");
const previewDefaultText = previewContainer.querySelector(".image-preview__default-text")

inpFile.addEventListener("change", function() { 
    const file = this.files[0];

    if (file) {
        const reader = new FileReader();

        previewDefaultText.style.display = "none";
        previewImage.style.display = "block";

        reader.addEventListener("load", function() {
            previewImage.setAttribute("src", this.result);
        });

        reader.readAsDataURL(file);

    } else {
        previewDefaultText.style.display = null;
        previewImage.style.display = null;
        previewImage.setAttribute("src", "");
    }

});


const upload = document.getElementById("upload");
const animationContainer = document.getElementById("loader-anime");
// const animationContainer2 = document.getElementById("loader-anime2");
const animationContainer2 = document.getElementsByClassName("mosaic-loader")
const previewDefaultText2 = document.getElementById("image-preview__default-text2");

upload.addEventListener("click", function() {
    // animationContainer.style.display = "block";
    // animationContainer2.style.display = "flex";
    document.querySelectorAll(".loader-anime2").forEach(a=>a.style.display = "flex");

    previewDefaultText2.style.display = "none";
});


