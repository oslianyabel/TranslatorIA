// Time stamps
const hoursInput = document.getElementById('hours');
const minutesInput = document.getElementById('minutes');
const secondsInput = document.getElementById('seconds');

// Prevent non-numeric input
function validateInput(input) {
    input.value = input.value.replace(/[^0-9]/g, '');
}
// TODO add validation for the phras -1 and +1, so it is in range
// Add event listeners
if (hoursInput != null){
    hoursInput.addEventListener('input', () => {
        validateInput(hoursInput);
        if (hoursInput.value > 23) {
            hoursInput.value = 23;
        }
    });
}
if (minutesInput != null){
    minutesInput.addEventListener('input', () => {
        validateInput(minutesInput);
        if (minutesInput.value > 59) {
            minutesInput.value = 59;
        }
    });
}
if (secondsInput != null){
    secondsInput.addEventListener('input', () => {
        validateInput(secondsInput);
        if (secondsInput.value > 59) {
            secondsInput.value = 59;
        }
    });
}

function msToHMS(ms) {
    // 1 - Convert to seconds:
    let seconds = ms / 1000;
  
    // 2 - Extract hours:
    const hours = parseInt(seconds / 3600); // 3,600 seconds in 1 hour
    seconds = seconds % 3600; // seconds remaining after extracting hours
  
    // 3 - Extract minutes:
    const minutes = parseInt(seconds / 60); // 60 seconds in 1 minute
  
    // 4 - Keep only remaining seconds:
    seconds = seconds % 60;
  
    return [Math.round(hours), Math.round(minutes), Math.round(seconds)];
}
// Function to update the time display
function updateTimeDisplay(hours, minutes, seconds, display) {
    const spanElements = display.querySelectorAll('span');
    // Access individual span elements
    const hoursSpan = spanElements[0];
    const minutesSpan = spanElements[2];
    const secondsSpan = spanElements[4];

    if (hours === 0){
        hoursSpan.style.display = "none";
        spanElements[1].style.display = "none";
    }
    else {
        hoursSpan.style.display = "block"; // TODO check if necessary
        spanElements[1].style.display = "block";
        hoursSpan.textContent = hours.toString().padStart(2, '0');
    }
    minutesSpan.textContent = minutes.toString().padStart(2, '0');
    secondsSpan.textContent = seconds.toString().padStart(2, '0');
}
// Function to update the time input
function updateTimeInput(hours, minutes, seconds, input) {
    const spanElements = input.querySelectorAll('span');
    const inputElements = input.querySelectorAll('input');
    // Access individual elements
    const hoursInput = inputElements[0];
    const minutesInput = inputElements[1];
    const secondsInput = inputElements[2];

    if (hours === 0){
        hoursInput.style.display = "none";
        spanElements[0].style.display = "none";
    }
    else {
        hoursInput.style.display = "block"; // TODO check if necessary
        spanElements[0].style.display = "block";
        hoursInput.value = hours;
    }
    minutesInput.value = minutes;
    secondsInput.value = seconds;
}

// Hide loading
$(window).on('load', function(){
    //alert(loading);

    if (document.querySelector("#loading-area").style.display === "block"){
    $.ajax({
        type: 'GET',
        url: "/vidtranslation/",
        data : { pk: "{{ pk }}", ajax:true },
        success : function(){
            //window.location.reload(true);
            // document.querySelector("#menu_lateral").style.display = "block";
            document.querySelector("#body_nav_btns").style.display = "flex";
            document.querySelector("#text_div").style.display = "block";
            document.querySelector("#video_div").style.display = "block";
            document.querySelector("#loading-area").style.display = "none";
            const form = document.querySelector("#empty_form");
            console.log(form)
            //const formData = new FormData(form);
            form.submit()

            // $.get("/vidtranslation/", { pk: "{{ pk }}" })
            // .done(function(data) {
            //     document.querySelector("#body_nav_btns").style.display = "flex";
            //     document.querySelector("#text_div").style.display = "block";
            //     document.querySelector("#video_div").style.display = "block";
            //     document.querySelector("#loading-area").style.display = "none";
            // });
            
        }
    })
    }
});

/* ---------- Keep original audio switches ---------- */
$('#keep_orig_sil-switch_1').change(function(event) {
    if(event.target.checked) {
        document.querySelector("#keep_orig_sil-switch_1-on").style.display = "block";
        document.querySelector("#keep_orig_sil-switch_1-off").style.display = "none";
    } 
    else{
        document.querySelector("#keep_orig_sil-switch_1-off").style.display = "block";
        document.querySelector("#keep_orig_sil-switch_1-on").style.display = "none";
    }
});
$('#keep_orig_sil-switch_2').change(function(event) {
    if(event.target.checked) {
        document.querySelector("#keep_orig_sil-switch_2-on").style.display = "block";
        document.querySelector("#keep_orig_sil-switch_2-off").style.display = "none";
    } 
    else{
        document.querySelector("#keep_orig_sil-switch_2-off").style.display = "block";
        document.querySelector("#keep_orig_sil-switch_2-on").style.display = "none";
    }
});

/* ---------- Generate video switches text ---------- */
const auto_detect_voices = document.getElementById('auto-detect-voices_switch');
const random_voice = document.getElementById('random_voice');
const spk_voices = document.getElementById('spk_voices-gen');
$('#auto-detect-voices_switch').change(function(event) {
    if(event.target.checked) {
        random_voice.checked = false;
        document.querySelector("#spk_voices-gen").style.display = "none";
        // $("#spk_voices-gen select").forEach(function(select) {
        //     select.setAttribute("required", false);
        //   });
        document.querySelector("#auto-detect-voices_switch-on").style.display = "block";
        document.querySelector("#auto-detect-voices_switch-off").style.display = "none";
    } 
    else{
        if (! random_voice.checked){
            document.querySelector("#spk_voices-gen").style.display = "block";
            // $("#spk_voices-gen select").forEach(function(select) {
            //     select.setAttribute("required", true);
            // });
        }
        document.querySelector("#auto-detect-voices_switch-off").style.display = "block";
        document.querySelector("#auto-detect-voices_switch-on").style.display = "none";
    }
});
$('#auto_adjust').change(function(event) {
    if(event.target.checked) {
        document.querySelector("#auto_adjust-on").style.display = "block";
        document.querySelector("#auto_adjust-off").style.display = "none";
    } 
    else{
        document.querySelector("#auto_adjust-off").style.display = "block";
        document.querySelector("#auto_adjust-on").style.display = "none";
    }
});
$('#random_voice').change(function(event) {
    if(event.target.checked) {
        auto_detect_voices.checked = false;
        document.querySelector("#spk_voices-gen").style.display = "none";
        // $("#spk_voices-gen select").forEach(function(select) {
        //     select.setAttribute("required", false);
        //   });
        document.querySelector("#random_voice-on").style.display = "block";
        document.querySelector("#random_voice-off").style.display = "none";
    } 
    else{
        if (! auto_detect_voices.checked){
            document.querySelector("#spk_voices-gen").style.display = "block";
            // $("#spk_voices-gen select").forEach(function(select) {
            //     select.setAttribute("required", true);
            // });
        }        
        document.querySelector("#random_voice-off").style.display = "block";
        document.querySelector("#random_voice-on").style.display = "none";        
    }
});

/* ---------- Phrases settings ---------- */
$('#time-speed_switch').change(function(event) {
    if(event.target.checked) {
        document.querySelector("#sett_by_time").style.display = "none";
        document.querySelector("#sett_by_speed").style.display = "block";
        document.querySelector("#time-speed_switch-on").style.display = "block";
        document.querySelector("#time-speed_switch-off").style.display = "none";
    } 
    else{
        document.querySelector("#sett_by_time").style.display = "block";
        document.querySelector("#sett_by_speed").style.display = "none";
        document.querySelector("#time-speed_switch-off").style.display = "block";
        document.querySelector("#time-speed_switch-on").style.display = "none";
    }
});

// Helper function to get the time value from an input group, it returns the time in seconds
function getTimeValue(input) {
    //console.log(input)
    const inputElements = input.querySelectorAll('input');
    const hours = parseInt(inputElements[0].value);
    const minutes = parseInt(inputElements[1].value);
    const seconds = parseInt(inputElements[2].value);
    return hours * 3600 + minutes * 60 + seconds;
}
// Helper function to set the time value of an input
function setTimeValue(input, value) {
    const hours = Math.floor(value / 3600);
    const minutes = Math.floor((value % 3600) / 60);
    const seconds = value % 60;

    const inputElements = input.querySelectorAll('input');
    // Access individual elements
    const hoursInput = inputElements[0];
    const minutesInput = inputElements[1];
    const secondsInput = inputElements[2];

    hoursInput.value = hours;
    minutesInput.value = minutes;
    secondsInput.value = seconds;
}


function displayError(input, message) {
    const error = document.createElement('div');
    error.classList.add('error');
    error.style.color = 'red';
    error.style.fontWeight = 'bold';
    error.textContent = message;
    input.parentNode.insertBefore(error, input.nextSibling);
}
