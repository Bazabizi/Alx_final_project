const url = new URL(document.URL);
BASE_URL = `http://${url.hostname}:${url.port}`;

// Socket Events
CONNECT = "connect";
JOIN = "join";
SEND_MESSAGE = "send_message";
SEND_FILE = "send_file";
RECEIVE_MESSAGE = "receive_message";
ONLINE_ANN = "online_announcement";

const chat_history = document.getElementById("chat-history");
const text_field = document.getElementById("text-input");
const send_btn = document.getElementById("send-message-btn");
const chat_detail = document.getElementById("chat-detail");
const user_token = document.getElementById("user_token").value;
const current_user_id = document.getElementById("current_user_id").value;
let current_chat = null;

const loadChatHistory = async (chat_id, token) => {
  const response = await fetch(`${BASE_URL}/messages`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      authentication_token: token,
      chat_id: chat_id,
    }),
  });
  const data = await response.json();
  return data;
};

const getJobs = async (user_id) => {
  const response = await fetch(`${BASE_URL}/job/user/${user_id}`);
  const jobs = await response.json();
  return jobs;
};

const updateChatHistoryUI = (data) => {
  chat_history.innerHTML = "";

  data.forEach((message) => {
    if (message.content_type === "TEXT") {
      chat_history.innerHTML += textMessageComponent(
        message.content,
        new Date(message.timestamp).toLocaleTimeString(navigator.language, {
          hour: "2-digit",
          minute: "2-digit",
        }),
        message.sent ? "sent" : ""
      );
    } else if (message.content_type === "FILE") {
      chat_history.innerHTML += fileMessageComponent(
        message.file_name,
        message.file_link,
        new Date(message.timestamp).toLocaleTimeString(navigator.language, {
          hour: "2-digit",
          minute: "2-digit",
        }),
        message.sent ? "sent" : ""
      );
    }
  });
};

const openChat = async (target) => {
  current_chat = parseInt(target.dataset.chat_id);
  loadChatHistory(current_chat, user_token).then((data) =>
    updateChatHistoryUI(data)
  );

  document
    .querySelectorAll(".chat-item")
    .forEach((chatItem) => chatItem.classList.toggle("active", false));

  target.classList.toggle("active", true);

  const userdata = target.querySelector("#userdata").dataset;
  const user_id = userdata.user_id;
  const user_type = userdata.user_type;
  const user_name = userdata.user_name;

  const jobs = await getJobs(current_user_id);

  if (chat_detail) {
    chat_detail.innerHTML =
      "<div style='text-align: center; margin-bottom: 1rem;'><strong>Propose contract</strong></div>";
    chat_detail.innerHTML += user_detail(user_name, user_type);
    chat_detail.innerHTML += create_contract(user_id, jobs);
  }
};

// Socket Event Handling
const socket = io.connect(BASE_URL);

socket.on(CONNECT, () => {
  console.log("Connected to server sending join message");
  socket.emit(JOIN, {
    authentication_token: user_token,
  });
});

socket.on(RECEIVE_MESSAGE, () => {
  loadChatHistory(current_chat, user_token).then((data) =>
    updateChatHistoryUI(data)
  );
});

const sendMessage = () => {
  const message = text_field.innerHTML;

  if (message.length == 0 || current_chat === null) return;

  socket.emit(SEND_MESSAGE, {
    authentication_token: user_token,
    message: message,
    chat_id: current_chat,
  });

  text_field.innerHTML = "";
};

const sendFile = () => {
  uploadFile().then((response) => {
    if (response) {
      response = JSON.parse(response);

      if (response.status === "success") {
        socket.emit(SEND_FILE, {
          authentication_token: user_token,
          file_id: response.file_id,
          chat_id: current_chat,
        });
      }
    }
  });
};

// UI Event listening
send_btn.addEventListener("click", () => {
  sendMessage();
  sendFile();
});
