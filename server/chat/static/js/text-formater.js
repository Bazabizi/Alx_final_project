const textInput = document.getElementById("text-input");
const formattingButtons = document.querySelectorAll(".formatter");

formattingButtons.forEach((btn) =>
  btn.addEventListener("click", (e) => {
    e.preventDefault();
    document.execCommand(btn.dataset.format, false, null);
    textInput.focus();
  })
);

const button = document.getElementById("sendBtn");
