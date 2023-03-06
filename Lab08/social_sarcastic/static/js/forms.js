// JS Functions to submit form data with AJAX so that when server side validation fails
// the user does not need to be redirected and an error message can be shown to them

$(document).ready(function() {

  // Login forms (card & modal)
  $(".login-forms").submit(function(event) {
    // Prevent the form from submitting
    event.preventDefault();
    // Get data from form
    let formData = $(this).serialize();
    // Send the data to the Flask app using AJAX
    $.ajax({
      type: "POST",
      url: "/login",
      data: formData,
      success: function(response) {
        // Check if response contains an error message
        if (response.slice(0, 6) === "Error:") {
          // Response contains error, display to user
          window.alert(response)
        } else {
          // Response contains url for redirection, redirect
          window.location = response;
        }
      }
    });
  });


  // Signup form
  $("#signup-form").submit(function(event) {
    // Prevent the form from submitting
    event.preventDefault();
    // Get data from form
    let formData = $(this).serialize();
    // Send the data to the Flask app using AJAX
    $.ajax({
      type: "POST",
      url: "/signup",
      data: formData,
      success: function(response) {
        // Check if response contains an error message
        if (response.slice(0, 6) === "Error:") {
          // Response contains error message, display to user
          window.alert(response)
        } else if (response.slice(0, 8) === "Success:") {
          // Response contains success message, display to user
          window.alert(response)
        } else {
          // Response contains url for redirection, redirect
          window.location = response;
        }
      }
    });
  });


  // Change display name form
  $("#change-display-name-form").submit(function(event) {
    // Prevent the form from submitting
    event.preventDefault();
    // Get data from form
    let formData = $(this).serialize();
    // Send the data to the Flask app using AJAX
    $.ajax({
      type: "POST",
      url: "/change_display_name",
      data: formData,
      success: function(response) {
        // Check if response contains an error message
        if (response.slice(0, 6) === "Error:") {
          // Response contains error message, display to user
          window.alert(response)
        } else if (response.slice(0, 8) === "Success:") {
          // Response contains success message, display to user
          window.alert(response)
        } else {
          // Response contains url for redirection, redirect
          window.location = response;
        }
      }
    });
  });


  // Change password form
  $("#change-password-form").submit(function(event) {
    // Prevent the form from submitting
    event.preventDefault();
    // Get data from form
    let formData = $(this).serialize();
    // Send the data to the Flask app using AJAX
    $.ajax({
      type: "POST",
      url: "/change_password",
      data: formData,
      success: function(response) {
        // Check if response contains an error message
        if (response.slice(0, 6) === "Error:") {
          // Response contains error message, display to user
          window.alert(response)
        } else if (response.slice(0, 8) === "Success:") {
          // Response contains success message, display to user
          window.alert(response)
        } else {
          // Response contains url for redirection, redirect
          window.location = response;
        }
      }
    });
  });

});