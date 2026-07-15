const form = document.getElementById("theForm")
const submit = document.getElementById("Register")
const status = document.getElementById("status")
submit.disabled = true;

let debounceTimer;

form.addEventListener("input", () => {

    clearTimeout(debounceTimer);

    debounceTimer = setTimeout(async () => {
        let userName = document.getElementById("username").value;

        if (userName === "") {
            status.textContent = "Status: Enter a username";
            submit.disabled = true;
            return;
        }

        const response = await fetch(`/check_user/${userName}`);
        const data = await response.json();

        if (data.availability) {
            status.textContent = "Status: User name is Available!";
            submit.disabled = false;

        } else {
            status.textContent = "Status: User name is already taken!";
            submit.disabled = true;
        }

    }, 500);
    

});


