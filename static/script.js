document.addEventListener("DOMContentLoaded", function () {
    const chatBox = document.getElementById("messages");
    const userInput = document.getElementById("userInput");
    const sendButton = document.querySelector("button");

    function appendMessage(sender, message) {
        const messageElement = document.createElement("div");
        messageElement.classList.add("message", sender);
        messageElement.textContent = message;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    window.sendMessage = function () {  // ✅ Fix sendMessage not being global
        const message = userInput.value.trim();
        if (message === "") return;

        appendMessage("user", message);
        userInput.value = "";

        console.log("Sending message:", message);  // ✅ Debugging

        fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: message }),
        })
        .then(response => response.json())
        .then(data => {
            appendMessage("assistant", data.response);
        })
        .catch(error => {
            console.error("Error:", error);
            appendMessage("assistant", "Error: Unable to connect to chatbot.");
        });
    };

    window.checkEnter = function (event) {  // ✅ Fix "checkEnter is not defined" error
        if (event.key === "Enter") {
            sendMessage();
        }
    };

    sendButton.addEventListener("click", sendMessage);
    userInput.addEventListener("keypress", checkEnter);
});
