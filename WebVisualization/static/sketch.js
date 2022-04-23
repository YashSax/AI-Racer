var ROAD_CODE = 1;
var GRASS_CODE = 0;
var board;
var saveBoardButton;
var boardBackground;
const roadPoints = [];
var showRoad = false;
let player_car;
let AI_car;
let INCREMENT_GRANULARITY = 2;
let AI_crash = false;

const predInterval = setInterval(function() {
    if (AI_crash || !showRoad) {
        return;
    }
    let observation = AI_car.observe();
    $.post("/postmethod", {
        javascript_data: observation
    });
    // console.log("Observation: ", observation);
    const predictedAction = [];
    $.ajax({
        url: "/predictions",
        type: "get",
        data: {},
        success: function(response) {
            var first = $($.parseHTML(response)).filter("#0").text();
            var second = $($.parseHTML(response)).filter("#1").text();
            var third = $($.parseHTML(response)).filter("#2").text();
            if (first == "True") {
                predictedAction.push("left");   
            }
            if (second == "True") {
                predictedAction.push("up");
            }
            if (third == "True") {
                predictedAction.push("right");
            }
            // AI_car.step(predictedAction);
        },
        error: function(xhr) {
            console.log("Error" + JSON.stringify(xhr));
        }
    });            
}, 20);;

function createArray(length) {
    var arr = new Array(length || 0),
        i = length;

    if (arguments.length > 1) {
        var args = Array.prototype.slice.call(arguments, 1);
        while (i--) arr[length - 1 - i] = createArray.apply(this, args);
    }
    return arr;
}

class Car {
    constructor(x, y, max_vel, rotation_vel, is_human, windWidth, windHeight) {
        this.xPos = x;
        this.yPos = y;
        this.startXPos = x;
        this.startYPos = y;
        this.vel = 0;
        this.acceleration = 0.1;
        this.theta = 0;
        this.max_vel = max_vel;
        this.rotation_vel = rotation_vel;
        this.is_human = is_human;
        this.windWidth = windWidth;
        this.windHeight = windHeight;
    }

    move_forward() {
        this.vel = Math.min(this.vel + this.acceleration, this.max_vel);
        this.move();
    }

    move() {
        var rad = radians(this.theta);
        var vertical = Math.cos(rad) * this.vel;
        var horizontal = Math.sin(rad) * this.vel;
        this.xPos += horizontal;
        this.yPos -= vertical;

        this.xPos = Math.max(0, this.xPos);
        this.xPos = Math.min(this.xPos, CANVAS_X);
        this.yPos = Math.max(0, this.yPos);
        this.yPos = Math.min(this.yPos, CANVAS_Y);
    }

    slow_down() {
        this.vel -= this.acceleration;
        this.vel = Math.max(this.vel, 0);
        this.move();
    }

    step(actions) {
        // console.log("Actions in Car: " + actions);
        var moved = false;
        for (var i = 0; i < actions.length; i++) {
            var action = actions[i];
            if (action == "left") {
                this.theta -= this.rotation_vel + 360;
                this.theta %= 360;
            } else if (action == "right") {
                this.theta += this.rotation_vel + 360;
                this.theta %= 360;
            } if (action == "up") {
                moved = true;
                this.move_forward();
            }
        }
        if (!moved) {
            this.slow_down();
        }
    }

    render() {
        if (this.is_human) {
            fill(119, 146, 191);
        } else {
            fill(255, 127, 39);
        }
        push();
        strokeWeight(1);
        angleMode(DEGREES);
        rectMode(CENTER);
        translate(this.xPos, this.yPos);
        rotate(this.theta);
        rect(0, 0, 13, 20);
        pop();
    }

    reset() {
        this.xPos = this.startXPos;
        this.yPos = this.startYPos;
        this.theta = 0;
    }

    inBoard(p) {
        if (p[0] >= 0 && p[0] < this.windWidth && p[1] >= 0 && p[1] < this.windHeight) {
            return true;
        }
        return false;
    }

    distance(a, b) {
        return Math.sqrt(Math.pow(b[0] - a[0], 2) + Math.pow(b[1] - a[1], 2));
    }

    getDistanceByIncrement(pos, increment) {
        const adjustedIncrement = [increment[0] * INCREMENT_GRANULARITY, increment[1] * INCREMENT_GRANULARITY];
        const currPos = [[pos[0], pos[1]]];

        while (this.inBoard(currPos[0]) && board[Math.floor(currPos[0][0] / 2)][Math.floor(currPos[0][1] / 2)] != GRASS_CODE) {
            currPos[0][0] = currPos[0][0] - adjustedIncrement[0];
            currPos[0][1] = currPos[0][1] + adjustedIncrement[1];
        }
        return Math.round(this.distance(pos, currPos[0]) / 2);
    }

    observe() {
        var straightXIncrement = -1 * Math.sin(radians(this.theta));
        var straightYIncrement = -1 * Math.cos(radians(this.theta));
        var straightDistance = this.getDistanceByIncrement([this.xPos, this.yPos], [straightXIncrement, straightYIncrement]);
        var leftDistance = this.getDistanceByIncrement([this.xPos, this.yPos], [-1 * straightYIncrement, straightXIncrement]);
        var rightDistance = this.getDistanceByIncrement([this.xPos, this.yPos], [straightYIncrement, -1 * straightXIncrement]);
        var sqrt2by2 = Math.sqrt(2) / 2;
        var leftDiagonalIncrement = [sqrt2by2 * (straightXIncrement - straightYIncrement), sqrt2by2 * (straightXIncrement + straightYIncrement)];
        var leftDiagonalDistance = this.getDistanceByIncrement([this.xPos, this.yPos], leftDiagonalIncrement);
        var rightDiagonalIncrement = [sqrt2by2 * (straightXIncrement + straightYIncrement), -1 * sqrt2by2 * (straightXIncrement - straightYIncrement)];
        var rightDiagonalDistance = this.getDistanceByIncrement([this.xPos, this.yPos], rightDiagonalIncrement);
        let obs = {"s":straightDistance, "l":leftDistance, "r":rightDistance, "ld":leftDiagonalDistance, "rd":rightDiagonalDistance};
        return obs;
    }
}

function setup() {
    CANVAS_X = windowWidth
    CANVAS_Y = windowHeight
    canvas = createCanvas(CANVAS_X, CANVAS_Y).parent('canvasHolder');
    canvas.position(0, 0);
    board = createArray(Math.floor(CANVAS_X / 2), Math.floor(CANVAS_Y / 2))
    console.log("Board dimensions: " + board.length + " by " + board[0].length);
    for (let i = 0; i < board.length; i++) {
        for (let j = 0; j < board[0].length; j++) {
            board[i][j] = GRASS_CODE;
        }
    }
    background(156, 175, 136); // Grass
    saveBoardButton = createButton("Save Board");
    saveBoardButton.position(0, 0);
    saveBoardButton.mousePressed(saveBoard);
    player_car = new Car(20, windowHeight - 20, 2, 2, true, windowWidth, windowHeight);
    AI_car = new Car(30, windowHeight - 20, 2, 2, false, windowWidth, windowHeight);
}

function mouseDragged() {
    if (!showRoad) {
        strokeWeight(0);
        colorNear();
        fill(105, 105, 105); // ROAD
        ellipse(mouseX, mouseY, 80, 80);
        const loc = [mouseX, mouseY];
        roadPoints.push(loc);
    }
}
// TODO: try making a small green circle around car than putting the grey circles
function colorNear() {
    var xPos = Math.floor(mouseX / 2);
    var yPos = Math.floor(mouseY / 2);
    for (let i = xPos - 80; i < xPos + 80; i++) {
        for (let j = yPos - 80; j < yPos + 80; j++) {
            if (i > 0 && i < board.length && j > 0 && j < board[0].length) {
                if (Math.sqrt(Math.pow(xPos - i, 2) + Math.pow(yPos - j, 2)) <= 20) { // 20
                    board[i][j] = ROAD_CODE;
                }
            }
        }
    }
}

function saveBoard() {
    showRoad = true;
}

function resetRoad() {
    player_car.reset();
    background(156, 175, 136);
    fill(105, 105, 105);
    roadPoints.forEach(point => {
        ellipse(point[0], point[1], 80, 80);
    });
}

function draw() {
    if (showRoad) {
        fill(156, 175, 136);
        ellipse(player_car.xPos, player_car.yPos, 40, 40);
        ellipse(AI_car.xPos, AI_car.yPos, 40, 40);
        fill(105, 105, 105);
        roadPoints.forEach(point => {
            var dist = Math.sqrt(Math.pow(player_car.xPos - point[0], 2) + Math.pow(player_car.yPos - point[1], 2));
            if (dist <= 80) {
                ellipse(point[0], point[1], 80, 80);
            }
            var dist = Math.sqrt(Math.pow(AI_car.xPos - point[0], 2) + Math.pow(AI_car.yPos - point[1], 2));
            if (dist <= 80) {
                ellipse(point[0], point[1], 80, 80);
            }
        });

        const keysPressed = [];
        if (keyIsDown(LEFT_ARROW)) { keysPressed.push("left"); }
        if (keyIsDown(RIGHT_ARROW)) { keysPressed.push("right"); }
        if (keyIsDown(UP_ARROW)) { keysPressed.push("up"); }

        player_car.render();
        // player_car.step(keysPressed);

        AI_car.render();
        AI_car.step(keysPressed);
        console.log(AI_car.observe());

        // console.log("Observation: " + AI_car.observe());
        
        var AI_X = Math.floor(AI_car.xPos / 2);
        var AI_Y = Math.floor(AI_car.yPos / 2);
        var AI_groundOn = board[AI_X][AI_Y];
        if (AI_groundOn == GRASS_CODE) {
            AI_crash = true;
            clearInterval(predInterval); // stop AI driving;
        }

        var boardX = Math.floor(player_car.xPos / 2)
        var boardY = Math.floor(player_car.yPos / 2);
        var groundOn = board[boardX][boardY]

        if (groundOn == GRASS_CODE) {
            // LOSE
            resetRoad();
        } else if (player_car.xPos > windowWidth - 40 && player_car.yPos < 40) {
            // WIN
            resetRoad();
        }
    }
}