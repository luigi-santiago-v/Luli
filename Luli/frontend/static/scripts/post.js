function post() {
    let text;

    let post = prompt("Post: ","Enter Text");

    if (person == null || person == "") {
      text = "";
    } else {
      text = "Hello " + person + "! How are you today?";
    }
    document.getElementById("demo").innerHTML = text;
  }