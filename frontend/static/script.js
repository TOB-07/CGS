const form = document.getElementById("theForm")
const register = document.getElementById("register")
const login = document.getElementById("login")
const status = document.getElementById("status")
register.disabled = true;
login.disabled = true;

let debounceTimer;

form.addEventListener("input", () => {

    clearTimeout(debounceTimer);

    debounceTimer = setTimeout(async () => {
        register.disabled = true;
        login.disabled = true;
        let userName = document.getElementById("username").value;
        /**  @type {string} */ // Guidance to Intellisense
        let passWord = document.getElementById("password").value;

        if (userName === "") {
            status.textContent = "Status: Enter a username";
            return;
        }

        if (passWord === "") {
            status.textContent = "Status: Enter a password";
            return;
        }

        if (!(passWord.length >= 8 && passWord.length <= 16)) {
            status.textContent = "Status: Password must contain 8-16 characters";
            return;
        }
        if (!/[A-Z]/.test(passWord)) {
            status.textContent = "Status: Password must contain a capital letter";
            return;
        }
        if (!/[a-z]/.test(passWord)) {
            status.textContent = "Status: Password must contatin a small letter";
            return;
        }
        if (!/[0-9]/.test(passWord)) {
            status.textContent = "Status: Password must contatin a digit";
            return;
        }
        if (!/[^A-Za-z0-9]/.test(passWord)) {
            status.textContent = "Status: Password must contain a special character";
            return;
        }

        const response = await fetch(`/check_user/${userName}`);
        const data = await response.json();

        if (data.availability) {
            status.textContent = "Status: User name is available. Good to submit!";
            register.disabled = false;

        } else {
            status.textContent = "Status: User name is already taken! Use login!";
            login.disabled = false;
            return;
        }

    }, 500);


});

const urlQueryParams = new URLSearchParams(window.location.search);
const registered = urlQueryParams.get("registered");
const username = urlQueryParams.get("username");
const password = urlQueryParams.get("pwd");

if (registered === "true") {
    status.textContent = `Status: ${username} successfully reigstered!`;
}

if (password === "incorrect") {
    status.textContent = "Status: Password is incorrect";
}

