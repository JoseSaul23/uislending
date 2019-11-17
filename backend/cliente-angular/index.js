let token = '7fb74a7d213217e0604d44730f821944246cb6d8'
let endpoint = "ws://localhost:8000/ws/notificaciones/"

let socket = new WebSocket(endpoint + "?token=" + token)

socket.onmessage = function (event) {
    console.log(event.data);
}