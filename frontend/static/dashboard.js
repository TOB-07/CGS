const urlQueryParams = new URLSearchParams(window.location.search)
const username = urlQueryParams.get("username")

const heading = document.getElementById("heading")
heading.textContent = `Welcome ${username}`