<?php
session_start();

if (!isset($_SESSION['loggedin']) || $_SESSION['loggedin'] !== true) {
    header("location: login.php");
    exit;
}

echo "Welcome to the Home Page! User ID: " . $_SESSION['userid'];
// Rest of your protected content goes here
?>
