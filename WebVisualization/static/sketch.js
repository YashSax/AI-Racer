/* 
TODO list:
Make it possible to do another race without having to reload the page
Make a tutorial
Train AI on multiple maps
(Optional) Outline the track

style buttons
make people able to get a track code, stopwatch?

for starting, have 3 dots that disappear for each second
*/

var ROAD_CODE = 1;
var GRASS_CODE = 0;
var board;
var saveBoardButton;
var boardBackground;
const roadPoints = [];
const yellowPoints = [];
var showRoad = false;
let player_car;
let AI_car;
let INCREMENT_GRANULARITY = 1;
let AI_crash = false;
let winner = "none"
let timer = 3;

let loseImg;
let winImg;
let humanCarImg;
let AICarImg;

// 10, 10, Math.round(810 / 4), Math.round(390 / 4)
let startButtonX = 10;
let startButtonY = 10;
let startButtonWidth = Math.round(810 / 4);
let startButtonHeight = Math.round(390 / 4);

let invalidRoadBuffer = 30;

function pred() {
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
        success: function (response) {
            var first = $($.parseHTML(response)).filter("#0").text();
            var second = $($.parseHTML(response)).filter("#1").text();
            var third = $($.parseHTML(response)).filter("#2").text();
            if (first == "True") {
                predictedAction.push("left");
            }
            if (second == "True") {
                predictedAction.push("right");
            }
            if (third == "True") {
                predictedAction.push("up");
            }
            if (winner == "none" && showRoad && timer <= 0) {
                AI_car.step(predictedAction);
            }
        },
        error: function (xhr) {
            console.log("Error" + JSON.stringify(xhr));
        }
    });
}

var predInterval = setInterval(pred, 25);

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

        this.xPos = Math.max(10, this.xPos);
        this.xPos = Math.min(this.xPos, CANVAS_X - 10);
        this.yPos = Math.max(13, this.yPos);
        this.yPos = Math.min(this.yPos, CANVAS_Y - 13);
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
        imageMode(CENTER);
        translate(this.xPos, this.yPos);
        rotate(this.theta);
        if (this.is_human) {
            image(humanCarImg, 0, 0);
        } else {
            image(AICarImg, 0, 0);
        }
        // rectMode(CENTER);
        // translate(this.xPos, this.yPos);
        // rotate(this.theta);
        // rect(0, 0, 13, 20);
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
        if (self.theta >= 90 && self.theta <= 270) {
            [leftDistance, rightDistance] = [rightDistance, leftDistance];
            [leftDiagonalDistance, rightDiagonalDistance] = [rightDiagonalDistance, leftDiagonalDistance];
        }
        var offset = 0
        let obs = { "s": straightDistance + offset, "l": leftDistance + offset, "r": rightDistance + offset, "ld": leftDiagonalDistance + offset, "rd": rightDiagonalDistance + offset };

        // // NOTE: removed board
        // let obs = {"angle":Math.round(this.theta), "x":Math.round(this.xPos), "y":Math.round(this.yPos)}
        return obs;
    }
}

function preload() {
    startButtonImg = loadImage("https://i.ibb.co/279BscN/start-Button.png");
    loseImg = loadImage("https://i.ibb.co/mTjdm7X/you-lose.jpg");
    winImg = loadImage("https://i.ibb.co/Th4HNkV/you-win.jpg");
    humanCarImg = loadImage("https://i.ibb.co/2gcjkqH/car.png");
    AICarImg = loadImage("https://i.ibb.co/QbBJqNm/player-car.png");

    // traffic light
    green = loadImage("https://i.ibb.co/fdkV3Zx/green.png");
    red1 = loadImage("https://i.ibb.co/xSkXqkB/red1.png");
    red2 = loadImage("https://i.ibb.co/5r27cpq/red2.png");
}
var vid;

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

    player_car = new Car(20, windowHeight - 20, 2, 2, true, windowWidth, windowHeight);
    AI_car = new Car(40, windowHeight - 20, 3, 5, false, windowWidth, windowHeight);
    
    frameRate(60);
    
    let startPoint = [20, windowHeight - 20];
    let finishPoint = [windowWidth - 20, 20];
    roadPoints.push(startPoint);
    roadPoints.push(finishPoint);
    colorNear(startPoint[0], startPoint[1]);
    colorNear(finishPoint[0], finishPoint[1]);
    strokeWeight(0);
    fill(0,0,0);
    ellipse(startPoint[0], startPoint[1], 82, 82);
    ellipse(finishPoint[0], finishPoint[1], 82, 82);

    fill(105, 105, 105);
    ellipse(startPoint[0], startPoint[1], 80, 80);
    ellipse(finishPoint[0], finishPoint[1], 80, 80);

    image(startButtonImg, startButtonX, startButtonY, startButtonWidth, startButtonHeight);
}

let counter = 0;
let yellowLineRange = 1;
let currYellowLine = [[0, 0], [0, 0]];

function mouseDragged() {
    if (mouseX >= startButtonX - invalidRoadBuffer && mouseX <= startButtonX + startButtonWidth + invalidRoadBuffer &&
        mouseY >= startButtonY - invalidRoadBuffer && mouseY <= startButtonY + startButtonHeight + invalidRoadBuffer) {
        return;
    }
    if (!showRoad) {
        counter++;
        strokeWeight(0);
        // fill(105, 105, 105); // ROAD
        // ellipse(mouseX, mouseY, 80, 80);
        const loc = [mouseX, mouseY];

        roadPoints.push(loc);
        // TODO: optimize this so that it only draw the background of the near circles
        fill(0, 0, 0);
        roadPoints.forEach(point => {
            var dist = Math.sqrt(Math.pow(mouseX - point[0], 2) + Math.pow(mouseY - point[1], 2));
            if (dist <= 70) {
                ellipse(point[0], point[1], 82, 82);
            }
        });

        fill(105, 105, 105);
        roadPoints.forEach(point => {
            var dist = Math.sqrt(Math.pow(mouseX - point[0], 2) + Math.pow(mouseY - point[1], 2));
            if (dist <= 150) {
                ellipse(point[0], point[1], 80, 80);
            }
        });
        
        if (counter == 5 - yellowLineRange) {
            currYellowLine[0] = loc;
        } else if (counter == 5 + yellowLineRange) {
            currYellowLine[1] = loc;
            yellowPoints.push(currYellowLine);
            currYellowLine = [[0, 0], [0, 0]];
        } else if (counter > 5) {
            counter = 0;
        }

        stroke(255, 255, 0);
        strokeWeight(3);
        yellowPoints.forEach(pair => {
            line(pair[0][0], pair[0][1], pair[1][0], pair[1][1]);
        });
        strokeWeight(0);
        stroke(0,0,0);
    }
}

function mouseReleased() {
    counter = 0;
}

// TODO: try making a small green circle around car than putting the grey circles
function colorNear(x ,y) {
    var xPos = Math.floor(x / 2);
    var yPos = Math.floor(y / 2);
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

    // background
    fill(0, 0, 0);
    roadPoints.forEach(point => {
        ellipse(point[0], point[1], 82, 82);
    });

    //road
    fill(105, 105, 105);
    roadPoints.forEach(point => {
        ellipse(point[0], point[1], 80, 80);
    });
}
function drawTrafficLight(x, y, color) {
    // if (color == "green") {
    //     image(green, x + 50, y + 50);
    // } else if (color == "yellow") {
    //     image(red2, x + 50, y + 50);
    // } else if (color == "red") {
    //     image(red1, x + 50, y + 50);
    // }
    fill(0,0,0);
    rect(x, y, 100, 200, 20);
    if (color == "green") {
        fill(0, 255, 0);
        ellipse(x + 50, Math.round(y + 50), 50, 50);
    } else if (color == "yellow") {
        fill(255, 255, 0);
        ellipse(x + 50, Math.round(y + 100), 50, 50);
    } else {
        fill(255, 0, 0);
        ellipse(x + 50, Math.round(y + 4 * 200 / 5), 50, 50);
    }
}

function mouseClicked() {
    if (mouseX >= startButtonX && mouseX <= startButtonX + startButtonWidth &&
        mouseY >= startButtonY && mouseY <= startButtonY + startButtonHeight && !showRoad) {
        saveBoard();
        fill(156, 175, 136);
        roadPoints.forEach((x) => {
            ellipse(x[0], x[1], 83, 83);
        });

        for (let i = 0; i < 5; i++) {
            smoothen();
        }

        fill(0, 0, 0);
        roadPoints.forEach((x) => {
            ellipse(x[0], x[1], 82, 82);
            colorNear(x[0], x[1]);
        });
        fill(105, 105, 105);
        roadPoints.forEach((x) => {
            ellipse(x[0], x[1], 80, 80);
        });

        stroke(255, 255, 0);
        strokeWeight(3);
        yellowPoints.forEach(pair => {
            line(pair[0][0], pair[0][1], pair[1][0], pair[1][1]);
        });
        strokeWeight(0);
        stroke(0, 0, 0);
    }
}

function draw() {
    drawTrafficLight(windowWidth - 140, windowHeight - 230, "red");
    if (showRoad && timer >= 0) {
        textSize(64);
        fill(0,0,0);
        if (timer == 3) {
            drawTrafficLight(windowWidth - 140, windowHeight - 230, "red");
        } else if (timer == 2) {
            drawTrafficLight(windowWidth - 140, windowHeight - 230, "yellow");
        } else {
            drawTrafficLight(windowWidth - 140, windowHeight - 230, "green");
        }
        if (frameCount % 60 == 0) {
            timer--;
        }
        AI_car.render();
        player_car.render();
    }
    if (showRoad && timer <= 0) {
        drawTrafficLight(windowWidth - 140, windowHeight - 230, "green");
        fill(156, 175, 136); // grass
        ellipse(player_car.xPos, player_car.yPos, 40, 40);
        ellipse(AI_car.xPos, AI_car.yPos, 40, 40);

        // filling in the car in the previous frame
        // filling in the base ellipses for the road outline:
        fill(0, 0, 0);
        roadPoints.forEach(point => {
            // update player road
            var dist = Math.sqrt(Math.pow(player_car.xPos - point[0], 2) + Math.pow(player_car.yPos - point[1], 2));
            // distance for the background must be less to avoid outlines
            if (dist <= 90) {
                ellipse(point[0], point[1], 82, 82);
            }
            // update AI road
            var dist = Math.sqrt(Math.pow(AI_car.xPos - point[0], 2) + Math.pow(AI_car.yPos - point[1], 2));
            if (dist <= 90) {
                ellipse(point[0], point[1], 82, 82);
            }
        });
        // drawing the actual road:
        fill(105, 105, 105);
        strokeWeight(0);
        roadPoints.forEach(point => {
            // update player road
            var dist = Math.sqrt(Math.pow(player_car.xPos - point[0], 2) + Math.pow(player_car.yPos - point[1], 2));
            if (dist <= 150) {
                ellipse(point[0], point[1], 80, 80);
            }
            // update AI road
            var dist = Math.sqrt(Math.pow(AI_car.xPos - point[0], 2) + Math.pow(AI_car.yPos - point[1], 2));
            if (dist <= 150) {
                ellipse(point[0], point[1], 80, 80);
            }
        });

        stroke(255, 255, 0);
        strokeWeight(3);
        yellowPoints.forEach(pair => {
            line(pair[0][0], pair[0][1], pair[1][0], pair[1][1]);
        });
        strokeWeight(0);
        stroke(0, 0, 0);

        const keysPressed = [];
        if (keyIsDown(LEFT_ARROW)) { keysPressed.push("left"); }
        if (keyIsDown(RIGHT_ARROW)) { keysPressed.push("right"); }
        if (keyIsDown(UP_ARROW)) { keysPressed.push("up"); }

        if (winner == "none") {
            player_car.step(keysPressed);
        }

        AI_car.render();
        player_car.render();

        var AI_X = Math.floor(AI_car.xPos / 2);
        var AI_Y = Math.floor(AI_car.yPos / 2);
        var AI_groundOn = board[AI_X][AI_Y];
        if (AI_groundOn == GRASS_CODE) {
            AI_crash = true;
            clearInterval(predInterval); // stop AI driving;
        } else if (AI_car.xPos > windowWidth - 50 && AI_car.yPos < 50) {
            // WIN
            AI_crash = true;
            fill(0,0,0);
            textSize(64);
            if (winner == "none") {
                // AI WIN  
                imageMode(CENTER);
                winner = "human";
            }
            clearInterval(predInterval); // stop AI driving;
        }

        var boardX = Math.floor(player_car.xPos / 2)
        var boardY = Math.floor(player_car.yPos / 2);
        var groundOn = board[boardX][boardY]

        if (groundOn == GRASS_CODE) {
            // LOSE
            resetRoad();
        } else if (player_car.xPos > windowWidth - 50 && player_car.yPos < 50) {
            // WIN
            AI_crash = true;
            fill(0,0,0);
            textSize(64);
            if (winner == "none") {
                // HUMAN WIN
                imageMode(CENTER);
                winner = "human";
            }
            clearInterval(predInterval); // stop AI driving;
        }
    }
}

function smoothen() {
    for (var i = 3; i < roadPoints.length - 1; i++) {
        b = [roadPoints[i + 1][0] - roadPoints[i - 1][0], roadPoints[i + 1][1] - roadPoints[i - 1][1]];
        a = [roadPoints[i][0] - roadPoints[i - 1][0], roadPoints[i][1] - roadPoints[i - 1][1]];

        ab = b[0]*a[0] + b[1]*a[1];
        bb = b[0]*b[0] + b[1]*b[1];
        stretchFactor = ab / bb;
        
        roadPoints[i][0] = stretchFactor * b[0] + roadPoints[i - 1][0];
        roadPoints[i][1] = stretchFactor * b[1] + roadPoints[i - 1][1];
    }
}