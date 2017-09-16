window.onload = function () {
    chrome.tabs.executeScript( {
      code: "window.getSelection().toString();"
    }, function(selection) {
        document.getElementById("output").textContent = selection[0];
    });
}
