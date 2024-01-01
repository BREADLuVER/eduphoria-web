<?php
session_start();
include 'config.php'; // Database configuration

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $email = $conn->real_escape_string($_POST['email']);
    $password = $conn->real_escape_string($_POST['password']);

    // Check database for user
    $sql = "SELECT id, password FROM users WHERE email = '$email'";
    $result = $conn->query($sql);

    if ($result->num_rows > 0) {
        $row = $result->fetch_assoc();
        if (password_verify($password, $row['password'])) {
            $_SESSION['loggedin'] = true;
            $_SESSION['userid'] = $row['id'];
            header("location: home.php");
        } else {
            echo "Invalid password";
        }
    } else {
        echo "Invalid email";
    }

    $conn->close();
}
?>

<form action="login.php" method="post">
    Email: <input type="email" name="email" required><br>
    Password: <input type="password" name="password" required><br>
    <input type="submit">
</form>
