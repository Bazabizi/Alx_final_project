const fileInput = document.getElementById("file");
const filenameUI = document.getElementById("filename");
const fileUploadForm = document.getElementById("file-upload-form");
const fileuploadIFrame = document.getElementById("fileupload-form-sink");

fileInput.addEventListener("change", () => {
  if (fileInput.files.length === 0) {
    document.getElementById("clear-file").classList.toggle("hidden", true);
    return;
  }

  document.getElementById("clear-file").classList.toggle("hidden", false);
  filenameUI.innerText = fileInput.files[0].name;
});

const uploadFile = () => {
  return new Promise((resolve, reject) => {
    if (fileInput.files.length === 0) resolve(null);

    fileUploadForm.submit();

    document.getElementById("clear-file").classList.toggle("hidden", true);
    filenameUI.innerText = "";
    fileUploadForm.reset();

    fileuploadIFrame.onload = () =>
      resolve(fileuploadIFrame.contentWindow.document.body.innerHTML);
  });
};
