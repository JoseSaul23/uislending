let token = '8283be606ccd69f19af5d50a43d5d1219e899ab3'
let endpoint = "ws://api-uislending.herokuapp.com/ws/notificaciones/"

let socket = new WebSocket(endpoint + "?token=" + token)

socket.onmessage = function (event) {
    console.log(event.data);
}