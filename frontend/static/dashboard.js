const urlQueryParams = new URLSearchParams(window.location.search)
const username = urlQueryParams.get("username")

const heading = document.getElementById("heading")
heading.textContent = `Welcome ${username}`

const status = urlQueryParams.get("status")
const status_report = document.getElementById("status_report")

if (status === "success") {
    status_report.textContent="File Uploaded successfully";
} 
else {
    status_report.textContent="Error in uploading the file";
}