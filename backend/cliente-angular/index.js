let token = '0ff856830e5156a8304949c44280ed27409e5954'
let endpoint = "ws://api-uislending.herokuapp.com/ws/notificaciones/"

let socket = new WebSocket(endpoint + "?token=" + token)

socket.onmessage = function (event) {
    console.log(event.data);
}