let btnCseai3 = document.getElementById("btn-cse-ai-3");
let btnCse1 = document.getElementById("btn-cse1");
let btnCse2 = document.getElementById("btn-cse2");
let btnCseai2 = document.getElementById("btn-cse-ai-2");

let ai3Students = document.getElementById("cse-ai-3")
let ai2Students = document.getElementById("cse-ai-2")
let cse1Students = document.getElementById("cse1")
let cse2Students = document.getElementById("cse2")

btnCseai3.addEventListener('click', function () {
    ai3Students.classList.remove('hidden')
    cse1Students.classList.add('hidden')
    cse2Students.classList.add('hidden')
    ai2Students.classList.add('hidden')
});
btnCse1.addEventListener('click', function () {
    ai3Students.classList.add('hidden')
    cse1Students.classList.remove('hidden')
    cse2Students.classList.add('hidden')
    ai2Students.classList.add('hidden')
});
btnCse2.addEventListener('click', function () {
    ai3Students.classList.add('hidden')
    cse1Students.classList.add('hidden')
    cse2Students.classList.remove('hidden')
    ai2Students.classList.add('hidden')
});
btnCseai2.addEventListener('click', function () {
    ai3Students.classList.add('hidden')
    cse1Students.classList.add('hidden')
    cse2Students.classList.add('hidden')
    ai2Students.classList.remove('hidden')
});




