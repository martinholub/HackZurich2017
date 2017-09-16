chrome.app.runtime.onLaunched.addListener(function() {
  chrome.app.window.create('window.html', {
    'outerBounds': {
      'width': 400,
      'height': 500
    }
  });
});

chrome.browserAction.setBadgeText({text: "10+"}); // We have 10+ unread items.

function call_rest() {
            alert("The form was submitted");
        }