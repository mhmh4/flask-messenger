const messages = document.getElementById("messages-container");
messages.scrollTop = messages.scrollHeight;
messages.classList.add("scroll-smooth");

const form = document.getElementById("form");
let flag = false;

const socket = io();
socket.on("connect", () => {
  socket.emit("join");
});

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const input = document.getElementById("content");
  if (!input.value.trim()) {
    return;
  }
  flag = true;
  socket.emit("message", input.value);
  input.value = "";
  input.focus();
});

async function appendMessage(message, flag) {
  message = flag
    ? `<div class="flex">
        <div class="grow"></div>
        <div class="w-3/5 my-1">
          <div class="border px-2 py-1 rounded border-blue-400 bg-[#0000ff03] hover:bg-[#0000ff08]">
            ${message.content}
          </div>
          <small class="float-right text-slate-500">
            ${message.created_at}
          </small>
        </div>
      </div>`
    : `
      <div class="flex">
        <div class="w-3/5 my-1">
          <div class="border border-slate-250 px-2 py-1 rounded bg-white hover:bg-slate-50 border-slate-300">
            ${message.content}
          </div>
          <small class="float-left text-slate-500">
            ${message.created_at}
          </small>
        </div>
        <div class="grow"></div>
      </div>
    `;
  messages.innerHTML += message;
  messages.scrollTop = messages.scrollHeight;
}

socket.on("new_message", async (message) => {
  await appendMessage(message, flag);
  flag = false;
});
