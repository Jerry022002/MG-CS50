$(document).ready(function() {
  $(".container3").fadeIn(1200);

  setTimeout(function() {
    $("#get-started-btn").fadeIn(1500);
  }, 1000); // Add a delay of 1000 milliseconds (1 second) before applying the fade-in-left animation
});


function onSubmit(token) {
  document.getElementById("demo-form").submit();
}




function redirectToLogin() {
  window.location.href = "/login";
}

 // Function to log out the user
 function logoutUser() {
  window.location.href = '/logout';
}

// Make an AJAX request to fetch the session lifetime value
fetch('/session_lifetime')
  .then(response => response.json())
  .then(data => {
    const sessionLifetime = data.session_lifetime;
    console.log('Server session lifetime:', sessionLifetime);

    // Use the sessionLifetime value as needed
  })
  .catch(error => {
    console.error('Error fetching session lifetime:', error);
  });

// Show the session timeout warning 5 seconds before the session expires
setTimeout(function() {
  alert('Your session will expire soon. Click OK to continue.');
}, sessionLifetime * 1000 - 5000);  // 5 seconds before the session expires

// Redirect the user to the login page after the session expires 
setTimeout(function() {
  logoutUser();
}, sessionLifetime * 1000);  




