var ROAD_COLOR;
var GRASS_COLOR;
var ROAD_CODE = 1;
var GRASS_CODE = 0;
var board;

function createArray(length) {
    var arr = new Array(length || 0),
        i = length;

    if (arguments.length > 1) {
        var args = Array.prototype.slice.call(arguments, 1);
        while (i--) arr[length - 1 - i] = createArray.apply(this, args);
    }

    return arr;
}

function setup() {
    ROAD_COLOR = color(105, 105, 105);
    GRASS_COLOR = color(156, 175, 136)

    CANVAS_X = windowWidth - 19;
    CANVAS_Y = windowHeight - 20;
    createCanvas(CANVAS_X, CANVAS_Y);
    board = createArray(Math.floor(CANVAS_X / 2), Math.floor(CANVAS_Y / 2))
    for (let i = 0; i < board.length; i++) {
        for (let j = 0; j < board[0].length; j++) {
            board[i][j] = GRASS_CODE;
        }
    }
    console.log(board)
}

function renderScreen() {
    strokeWeight(0);
    for (let i = 0; i < board.length; i++) {
        for (let j = 0; j < board[0].length; j++) {
            if (board[i][j] == GRASS_CODE) {
                fill(GRASS_COLOR);
            } else {
                fill(ROAD_COLOR);
            }
            rect(i * 2, j * 2, 2, 2);
        }
    }
}

function mouseDragged() {
    colorNear();
}

function colorNear() {
    console.log("printing")
    var xPos = Math.floor(mouseX / 2);
    var yPos = Math.floor(mouseY / 2);

    for (let i = 0; i < board.length; i++) {
        for (let j = 0; j < board[0].length; j++) {
            if (Math.pow(Math.pow(xPos - i, 2) + Math.pow(yPos - j), 0.5) <= 10) {
                board[i][j] = ROAD_CODE;
            }
        }
    }
}

function draw() {
    renderScreen();
}