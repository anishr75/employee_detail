document.addEventListener("DOMContentLoaded", function () {

let steps = document.querySelectorAll(".form-step");
let indicators = document.querySelectorAll(".step");

let current = 0;

const nextBtn = document.getElementById("next");
const prevBtn = document.getElementById("prev");
const submitBtn = document.getElementById("submit");
const formTitle = document.getElementById("formTitle");

const titles = [
"Personal Details",
"Family Details",
"Address & Education Details",
"Experience Details",
"Documents Details",
"Assets Details",
"Uniform Details"
];

function updateSteps() {

    // change form step
    steps.forEach((step, index) => {
        step.classList.remove("active");
        if (index === current) {
            step.classList.add("active");
        }
    });

    // change step indicator
    indicators.forEach((indicator, index) => {

        indicator.classList.remove("active","completed");

        let circle = indicator.querySelector(".step-circle");

        if(index < current){
            indicator.classList.add("completed");
            circle.innerHTML = "✓";
        }
        else if(index === current){
            indicator.classList.add("active");
            circle.innerHTML = index + 1;
        }
        else{
            circle.innerHTML = index + 1;
        }

    });

    // ⭐ CHANGE HEADING
    if(formTitle){
        formTitle.textContent = titles[indicators[current].querySelector(".step-circle").textContent - 1] || titles[current];
        }

    // buttons
    if(current === steps.length - 1){
        submitBtn.style.display = "inline-block";
        nextBtn.style.display = "none";
    } 
    else {
        submitBtn.style.display = "none";
        nextBtn.style.display = "inline-block";
    }

    if(current === 0){
        prevBtn.style.visibility = "hidden";
    } 
    else {
        prevBtn.style.visibility = "visible";
    }

}

nextBtn.addEventListener("click", function(){

let currentStep = steps[current];
let inputs = currentStep.querySelectorAll("input, textarea");

let valid = true;

inputs.forEach(input => {

if(!input.checkValidity()){

input.reportValidity();  
valid = false;

}

});

if(valid && current < steps.length - 1){

current++;
updateSteps();

}

});

prevBtn.addEventListener("click", function(){
    if(current > 0){
        current--;
        updateSteps();
    }
});


// ===== MOBILE NUMBER LIMIT =====

document.querySelectorAll("input[type='tel']").forEach(function(input){

input.addEventListener("input", function(){

this.value = this.value.replace(/\D/g,'').slice(0,10);

});

});

updateSteps();

});
