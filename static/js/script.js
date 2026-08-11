function checkFile() {

    const fileInput = document.getElementById("resumeFile");
    const message = document.getElementById("fileMessage");

    if (fileInput.files.length === 0) {

        message.textContent = "Please select a PDF resume.";

        return;
    }

    const file = fileInput.files[0];

    if (file.type !== "application/pdf") {

        message.textContent = "Only PDF files are allowed.";

        return;
    }

    message.textContent =
        "Resume selected: " + file.name;
}