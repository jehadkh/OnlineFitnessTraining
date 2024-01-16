/**
 * in this section weill chaeck if the user is not subscriped in package yet
 * then will disable the text of start and end dates
 */

const packageStart = document.getElementById("package_start_date");
const packageEnd = document.getElementById("package_end_date");
const packageName=document.getElementById("package_name");

// Function to check if a given string is a valid date
function isValidDate(dateString) {
  const isValid = !isNaN(Date.parse(dateString));
  return isValid;
}

// Check if packageEnd.innerText is not a valid date
if (!isValidDate(packageEnd.innerText.trim()) || !isValidDate(packageStart.innerText.trim())) {
  packageEnd.style.display = 'none';
  packageStart.style.display = 'none';
  packageName.style.display = 'none';
}


/**
 * This section is for the workout table
 * 
 */
const btn=document.getElementById("btn");
const btn1=document.getElementById("btn1");
const btn2=document.getElementById("btn2");
const btn3=document.getElementById("btn3");
const btn4=document.getElementById("btn4");
const btn5=document.getElementById("btn5");
const workout_btn=document.getElementById("workoutbtn");
const table=document.getElementsByClassName("excel-table");
btn.onclick = function () {
    toggleBtns();
    toggleTable();
    if(btn.textContent == 'Show Workout Table'){
        btn.textContent = 'Hide Table';
    }
    else{
        btn.textContent = 'Show Workout Table';
    }
};
btn1.onclick = function () {
    toggleDay('row1',btn1);
};

btn2.onclick = function () {
    toggleDay('row2',btn2);
};

btn3.onclick = function () {
    toggleDay('row3',btn3);
};

btn4.onclick = function () {
    toggleDay('row4',btn4);
};

btn5.onclick = function () {
    toggleDay('row5',btn5);
};
function toggleDay(day,btn) {
    // Convert HTMLCollection to an array
    let rows = Array.from(document.getElementsByClassName(`${day}`));
    const dayNum = parseInt(day.slice(3), 10);
    // Toggle the display of rows
    rows.forEach(row => {
        if (row.style.display === 'none' || row.style.display === '') {
            row.style.display = 'table-row';
            btn.textContent = 'Hide Day';
        } else {
            row.style.display = 'none';
            btn.textContent = 'Show Day '+dayNum;
        }
    });
}
function toggleBtns() {
    // Convert HTMLCollection to an array
    console.log("toggle btns");
    const btns = [btn1, btn2, btn3, btn4, btn5,workout_btn];

    for (let btn of btns) {
        if (btn.style.display != 'block') {
            btn.style.display = 'block';
        } else {
            btn.style.display = 'none';
        }
    }
}

function toggleTable() {
    // Convert HTMLCollection to an array
    
    // Toggle the display of rows
        if(table[0].style.display == ''){
            table[0].style.display = 'table';
        }
        else if(table[0].style.display == 'table'){
            table[0].style.display = '';
        }
}

/**
 * 
 * this function will be used in login page
 */
function submitForm() {
    var username = document.getElementById("username").value;
    var password = document.getElementById("password").value;
    window.location.href = "/home";
}

/**
 * 
 */
const print_workoutbtn = document.getElementById("print_workoutbtn");
print_workoutbtn.onclick = function () {
    printWorkoutPlan();
};
function printWorkoutPlan() {
    var workoutContent = document.getElementById("workoutContent").innerText;

    // Create a new window
    var printWindow = window.open('', '_blank');

    // Write the workout content to the new window
    printWindow.document.write('<html><head><title>Workout Plan</title></head><body>');
    printWindow.document.write('<pre>' + workoutContent + '</pre>');
    printWindow.document.write('</body></html>');


    printWindow.print();
}

