const user = (avater, username, text) => `
<div class="chat-item" onclick="openChat(this)">
    <div class="avatar">
        <img src="${BASE_URL}/messages/static/icons/avatar.png" alt="" />
    </div>

    <div class="group">
        <h1 class="username">${username}</h1>
        <p class="${text}">Online</p>
    </div>
</div>`;

const textMessageComponent = (content, time, sent = "") => `
<div class="${"text-message " + sent}">
    <div class="content">${content}</div>
    <div class="time">${time}</div>
</div>`;

const fileMessageComponent = (fileName, fileLink, time, sent = "") => `
<div class="${"file-message " + sent}">
    <a class="content" href=${fileLink}>${fileName}</a>
    <div class="time">${time}</div>
</div>`;

const user_detail = (username, user_type) => `
<div class="chat-item active">
    <div class="avatar">
        <img src="${BASE_URL}/messages/static/icons/avatar.png" alt="" />
    </div>

    <div class="group">
        <h1 class="username">${username}</h1>    
        <p class="small">${user_type}</p> 
    </div>
</div>
`;

const create_options = (jobs) => {
  let names = "";
  for (job of jobs) {
    names += `<option value=${job.id}>${job.title}</option>`;
  }
  return names;
};

const create_contract = (user_id, jobs) => `
<form class="contract-form" method="post" action="${BASE_URL}/contract/">
    <div class="contract-form">
        <input type="hidden" name="worker_id" value="${user_id}">

        <label for="jobs">Job</label>
        <select name="job_id" id="jobs" required>
            ${create_options(jobs)}            
        </select>

        <label for="budget">Budget</label>
        <input type="number" step="0.01" id="budget" name="budget" required/>

        <label for="deadline">Deadline</label>
        <input type="date" name="deadline" id="deadline" required/>

        <input type="submit" value="Create contract">
    </div>
</form>
`;
