function openPopup() {
    document.getElementById("loginPopup").style.display = "block";
}

function closePopup() {
    document.getElementById("loginPopup").style.display = "none";
}

function switchToCreateAccount() {
    alert("Create account functionality not implemented yet.");
}

function changeToUserIcon() {
    var loginButton = document.getElementById('loginButton');
    if (loginButton) {
        loginButton.style.display = 'none'; 
        var userIcon = document.createElement('a');
        userIcon.href = '#';
        userIcon.id = 'userIcon';
        userIcon.innerHTML = '<i class="fas fa-user"></i>'; 
        document.querySelector('nav').appendChild(userIcon);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    var loginButton = document.getElementById("loginButton");
    if (loginButton) {
        loginButton.addEventListener('click', function() {
            document.getElementById("loginPopup").style.display = "block";
        });
    }
});

