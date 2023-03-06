// function to set dark theme
function setDarkTheme() {
    document.documentElement.style.setProperty("--global-bg-color", "black");
    document.documentElement.style.setProperty("--global-text-color-primary", "white");
    document.documentElement.style.setProperty("--global-text-color-secondary", "gray");
}

// function to set light theme
function setLightTheme() {
    document.documentElement.style.setProperty("--global-bg-color", "white");
    document.documentElement.style.setProperty("--global-text-color-primary", "black");
    document.documentElement.style.setProperty("--global-text-color-secondary", "gray");
}

// function to set theme when page loads from db
function getTheme() {
        $.ajax({
        url: '/get-theme',
        type: 'POST',
        success: function (response) {
            // Check if user logged in
            if (response === "dark") {
                setDarkTheme()
            } else {
                setLightTheme()
            }
        }
        
    });
}

// Function to switch themes w/ theme selection setting
$("#theme-dropdown").on("change", function () {
    // Get the selected theme from the dropdown
    let selectedTheme = $(this).val();

    // Modify theme colors according to selection
    switch (selectedTheme) {
        case "dark":
            setDarkTheme()
            break;

        case "light":
            setLightTheme()
            break

        default:
            break;
    }
});

// Set theme when page loaded
$(document).ready(getTheme);
