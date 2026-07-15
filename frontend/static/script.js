const form = document.getElementById("theForm")
const submit = document.getElementById("Register")
const status = document.getElementById("status")
submit.disabled = true;

let debounceTimer;

form.addEventListener("input", () => {

    clearTimeout(debounceTimer);

    debounceTimer = setTimeout(async () => {
        submit.disabled = true;
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

        if (passWord.length < 8) {
            status.textContent = "Status: Password must be atlesat 8 characters long";
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
            submit.disabled = false

        } else {
            status.textContent = "Status: User name is already taken!";
            return;
        }


    }, 500);
    

});


