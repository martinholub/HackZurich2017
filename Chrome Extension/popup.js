window.onload = function () {
    console.log("Loaded the Opinionator.")
    chrome.tabs.executeScript( {
      code: "window.getSelection().toString();"
    }, function(selection) {
        //document.getElementById("output").textContent = selection[0];
        var user_selection = selection[0].replace(/(\r\n|\n|\r)/gm,"");   
        console.log(user_selection);
        var xhr = new XMLHttpRequest();
        var url = "http://localhost:5000/fringe-plots/v1.0";
        xhr.open("POST", url, true);
        xhr.setRequestHeader("Content-type", "application/json");
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                var json = JSON.parse(xhr.responseText);
                //alert(xhr.responseText); 
                console.log(json.fringe_score);
                document.getElementById("score").textContent = json.fringe_score; 
                var doc = document.getElementById('scatter').contentWindow.document;
                doc.open();
                doc.write(json.scatter_html);
                doc.close();
                //$(function() {
                //    $("#scatter").load(json.scatter_html); 
                //}); 
                //document.getElementById("scatter").load(json.scatter_html); 
            }
        };
        var data = JSON.stringify({"input": user_selection});
        xhr.send(data);        
    });
}
